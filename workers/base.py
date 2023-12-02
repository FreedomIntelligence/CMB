import pdb
import torch
from torch.utils.data import Dataset, DataLoader
import json
from accelerate import Accelerator
from dataclasses import dataclass
from accelerate import Accelerator
from copy import deepcopy

from peft import PeftModel
from transformers import (
    AutoModel, AutoModelForCausalLM, 
    AutoTokenizer, LlamaTokenizer,
    AutoConfig,
    
)


@dataclass
class BaseWorker():
    """
    The base class of each model worker.
    """
    cfg: dict
    input_pth: str
    output_pth: str
    batch_size: int 
    use_cot: bool = False
    use_qa: bool = False
    generate_fewshot_examples_only: bool = False
    use_fewshot: bool = False,

    def __post_init__(self):
        if self.generate_fewshot_examples_only: # no need to do post_init if we only need to generate fewshot examples
            return
        self.print_in_main(f'loading config: {self.cfg.load}')
        self.model, self.tokenizer = self.load_model_and_tokenizer(self.cfg.load)
        self.device = self.cfg.load.device
        self.accelerator = Accelerator()
        self.prompt_wrapper = PromptWrapper(
            self.tokenizer,
            self.instruction_template_with_fewshot if self.use_fewshot else self.instruction_template,
            conv_collater=self.collate_conv,
            use_cot=self.use_cot,
        )
        self.wrap_model()
        self.init_generation_config(self.cfg)
        self.init_dataloader(self.input_pth, self.batch_size)
        self.init_writer(self.output_pth)
    

    @classmethod
    def from_config(
        cls, 
        cfg, 
        input_pth: str = '',
        output_pth: str = '',
        batch_size = 1,
        use_qa = False, 
        use_cot = False,
        generate_fewshot_examples_only = False,
        use_fewshot = False,
        ):
        assert cfg.get('load', None) is not None
        
        return cls(
            cfg,             
            input_pth,
            output_pth,
            batch_size, 
            use_cot = use_cot,
            use_qa = use_qa, 
            generate_fewshot_examples_only = generate_fewshot_examples_only,
            use_fewshot = use_fewshot,
        )


    def load_model_and_tokenizer(self, load_config):
        # model = ...
        # return model, tokenizer,
        raise NotImplementedError


    @property
    def system_prompt(self,):
        return "" # no placeholder is needed
    @property
    def instruction_template(self,):
        return "" # with role and placeholder
    @property
    def instruction_template_with_fewshot(self,):
        return "" # with role and placeholder
    
    @property
    def query_prompt_1(self):
        return "以下是中国{exam_type}中{exam_class}考试的一道{question_type}，请分析每个选项，并最后给出答案。\n{question}\n{option_str}"
    @property
    def query_prompt_2(self):
        return "以下是中国{exam_type}中{exam_class}考试的一道{question_type}，不需要做任何分析和解释，直接输出答案选项。\n{question}\n{option_str}"
    @property
    def fewshot_prompt(self, ):
        '''the string that starts the fewshot example.
        default: `""`'''
        return ""
    @property
    def fewshot_separator(self, ):
        '''the string that separates fewshot examples.
        default: `""`'''
        return ""
    
    @property
    def fewshot_template(self):
        raise NotImplementedError
    
    def collate_conv(self, data, convs):
        raise NotImplementedError
    
    def init_generation_config(self, config):
        if config.generation_config.get('num_return_sequences', None) is None:
            config.generation_config['num_return_sequences'] = 1
        elif config.generation_config.get('num_return_sequences', 1) > 1 and config.generation_config.get('do_sample', False):
            self.print_in_main('`num_return_sequences` must be 1 when using `do_sample=True`. Setting `num_return_sequences=1`')
            config.generation_config['num_return_sequences'] = 1

        if self.use_qa:
            config.generation_config['repetition_penalty'] = 1.1
        
        self.generation_config = config.generation_config

        if (self.tokenizer.pad_token_id is None) and (self.tokenizer.eos_token_id is not None):
            self.print_in_main('warning: No pad_token in the config file. Setting pad_token_id to eos_token_id')
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
            assert self.tokenizer.pad_token_id == self.tokenizer.eos_token_id
        self.print_in_main(f'Generation config: {self.generation_config}')

    def init_dataloader(self, input_pth, batch_size):
        dataset = MyDataset(input_pth)
        dataloader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=False,
            drop_last=False,
            collate_fn=dataset.collate_fn,
        )
        self.dataloader = dataloader 
        self.wrap_dataloader()

    def wrap_dataloader(self):
        self.dataloader = self.accelerator.prepare(self.dataloader)

    def wrap_model(self,):
        self.model = self.accelerator.prepare(self.model)

    def unwrap_model(self,): # this is NOT inplace
        return self.accelerator.unwrap_model(self.model)
    
    def init_writer(self, output_pth):
        if self.is_main_process:
            self.writer = open(output_pth, "w", encoding='utf-8')
    def is_main_process(self):
        return self.accelerator.is_main_process
    def print_in_main(self, *args, **kwargs):
        if self.is_main_process:
            print(*args, **kwargs)

    def close(self,):
        if self.accelerator.is_main_process:
            self.writer.close()
    
    @torch.no_grad()
    def generate_batch(self, batch: list):
        r"""
        Args:
            batch (`List[dict]`):
                a list of raw data.
        Returns:
            outputs (`List[str]`):
                a list of generated output from the model.
        Usage:
            runner.generate(prompts)
        """

        if self.use_qa:
            batch, lines = self.prompt_wrapper.wrap_conv(batch) 
        else:
            batch, lines = self.prompt_wrapper.wrap(batch) 
        inputs = self.tokenizer(batch, padding=True, truncation=True, return_tensors="pt").to(self.device)
        self.prompt_wrapper.lengths = inputs.input_ids.shape[1]
        outputs = self.unwrap_model().generate( **inputs, **self.generation_config)
        outputs = self.prompt_wrapper.unwrap(outputs, self.generation_config.get('num_return_sequences', 1))
        
        return outputs, lines


    def get_single_query(self, datum, use_cot):
        datum["option_str"] = "\n".join(
            [f"{k}. {v}" for k, v in datum["option"].items() if len(v) > 1]
        )
        if use_cot:
            query = self.query_prompt_1.format_map(datum)
        else:
            query = self.query_prompt_2.format_map(datum)

        return query
    
    def format_fewshot_user_and_gpt(self, item: dict, use_cot):
        user = self.get_single_query(item, use_cot)
        explanation = item["explanation"]
        answer = item["answer"]

        if use_cot:
            # gpt = '[答案]\n' + "\n".join([f'{answer_item}. ' + item["option"][answer_item] for answer_item in answer]) + '\n'
            # gpt += f"[思考过程]\n{explanation}\n[结论]\n所以答案是{answer}。"
            gpt = f"{explanation}所以答案是{answer}。"
        else:
            gpt = f'答案是{answer}。'

        ''' zero-shot
        {role1}:
        以下是考试题，请给答案。
        李时珍写了啥？
        B. 黄帝内经
        C. 本草纲目
        {role2}
        本草纲目是李时珍写的。所以答案是C。
        '''

        ''' few-shot
        {role1}:
        以下是考试题，请给答案。
        李时珍写了啥？
        B. 黄帝内经
        C. 本草纲目
        {role2}
        答案是C。
        '''
        return user, gpt
    
    def generate_fewshot_examples(self, data: list[dict], use_cot=False):
        """
        Generate a fewshot prompt given a list of data.
        Note that the roles are already in the fewshot examples.
        Be careful not to add any extra roles in the final query that is input to an LLM.
        """
        prompt = self.fewshot_prompt
        for item in data:
            user, gpt = self.format_fewshot_user_and_gpt(item, use_cot)
            prompt += self.fewshot_template.format(user=user, gpt=gpt) + self.fewshot_separator
        return prompt
    


class PromptWrapper():
    def __init__(
            self, 
            tokenizer, 
            instruction_template, 
            conv_collater,
            use_cot=False
    ):

        self.instruction_template = instruction_template

        self.question_template = self.get_question_template(use_cot=use_cot)

        if '{fewshot_examples}' in self.instruction_template:
            # use fewshot examples
            # keep the fewshot placeholder, since examples are sample-specific 
            self.input_template = self.instruction_template.format(instruction=self.question_template, fewshot_examples='{fewshot_examples}') 
        else:
            self.input_template = self.instruction_template.format(instruction=self.question_template)

        self.conv_collater = conv_collater # for multi-turn QA only, implemented for each model
        self.tokenizer = tokenizer


    def get_system_template(self, t):
        if t.strip() == '':
            return '{instruction}'
        else:
            try:
                t.format(instruction='')
            except:
                raise Exception('there must be a {instruction} placeholder in the system template')
        return t
    
    def get_question_template(self, use_cot):
        if use_cot:
            return "以下是中国{exam_type}中{exam_class}考试的一道{question_type}，请分析每个选项，并最后给出答案。\n{question}\n{option_str}"
        else:
            return "以下是中国{exam_type}中{exam_class}考试的一道{question_type}，不需要做任何分析和解释，直接输出答案选项。\n{question}\n{option_str}"

    def wrap(self, data: list[dict]):
        '''
        data.keys(): ['id', 'exam_type', 'exam_class', 'question_type', 'question', 'option']. These are the raw data.
        We still need 'option_str'.
        '''
        res = []
        lines = []
        for line in data:
            line["option_str"] = "\n".join(
                [f"{k}. {v}" for k, v in line["option"].items() if len(v) > 1]
            )
            query = self.input_template.format_map(line)
            line['query'] = query

            res.append(query)
            lines.append(line)
        
        return res, lines
    
    def wrap_conv(self, data: list[dict]): # add
        lines = []
        res = []
        for line in data:
            # print(line)
            collated, partial_qa = self.conv_collater(line)
            # collated: ['Q', 'QAQ', 'QAQAQ', ...]
            # partial_qa: [
            #   [{'q': 'q'}], 
            #   [{'q': 'q', 'a': 'a'}, {'q'}], 
            #   [{'q': 'q', 'a': 'a'}, {'q': 'q', 'a': 'a'}, {'q': 'q'}]
            # ]
            res.extend(collated) # 1d list
            lines.extend(partial_qa)           
        return res, lines

    def unwrap(self, outputs, num_return_sequences):        
        batch_return = []
        responses_list = []
        for i in range(len(outputs)):
            # sample_idx = i // num_return_sequences
            output = outputs[i][self.lengths: ] # slicing on token level
            output = self.tokenizer.decode(output, skip_special_tokens=True)

            batch_return.append(output)
            if i % num_return_sequences == num_return_sequences - 1:
                responses_list.append(batch_return)
                batch_return = []
        return responses_list


class MyDataset(Dataset):
    def __init__(self, input_path):
        # data = []
        with open(input_path) as f:
            data = json.load(f)
        print(f"loading {len(data)} data from {input_path}")
        self.data = data


    def __getitem__(self, index):
        item: dict = self.data[index]
        return item

    def __len__(self):
        return len(self.data)

    def collate_fn(self, batch):
        # print(batch); exit()
        '''
        [id: '', title: '', description: '', QA_pairs: [
            {question: '', answer: ''},
            {question: '', answer: ''},
        ]]
        '''
        return batch


