
from .base import *


class ChatGLM3Worker(BaseWorker):


    def load_model_and_tokenizer(self, load_config):
        hf_model_config = {"pretrained_model_name_or_path": load_config['config_dir'],'trust_remote_code': True, 'low_cpu_mem_usage': True}
        hf_tokenizer_config = {"pretrained_model_name_or_path": load_config['config_dir'], 'padding_side': 'left', 'trust_remote_code': True}

        device = load_config.get('device', 'cuda')
        precision = load_config.get('precision', 'fp16')

        assert device == "cuda", 'only supports CUDA inference'
        assert precision in ['fp16', 'fp32'], 'Only supports fp16/32 for now'
        if precision == 'fp16':
            hf_model_config.update({"torch_dtype": torch.float16})

        from .chatglm3_modeling import ChatGLMForConditionalGeneration
        model = ChatGLMForConditionalGeneration.from_pretrained(**hf_model_config)
        tokenizer = AutoTokenizer.from_pretrained(**hf_tokenizer_config)
        model.eval()
        return model, tokenizer

    @property
    def system_prompt(self):
        return ""
    @property
    def instruction_template(self,):
        return self.system_prompt + '问：{instruction}\n答：'
    @property
    def instruction_template_with_fewshot(self,):
        return self.system_prompt + '{fewshot_examples}问：{instruction}\n答：'
    @property
    def fewshot_template(self,):
        return "[Round {round}]\n问：{user}\n答：{gpt}\n"
    
    def generate_fewshot_examples(self, data: list[dict], use_cot=False):
        """Generate a fewshot prompt given a list of data"""
        prompt = self.fewshot_prompt
        for round, item in enumerate(data):
            user, gpt = self.format_fewshot_user_and_gpt(item, use_cot)
            prompt += self.fewshot_template.format(round=round, user=user, gpt=gpt) + self.fewshot_separator
        return prompt
    
    
    def collate_conv(self, data):
        returned = []
        partial_qas = []
        line = self.system_prompt
        
        id = data['id']
        title = data['title']
        description = data['description']
        convs = data['QA_pairs']

        for i, conv in enumerate(convs):
            if i == 0:
                user = description + conv['question']
                line += f'[Round {i}]\n问：{user}\n'
                returned.append(line.replace('[Round 0]\n', '') + '答：') # do not include round information if there is only one question
            else:
                user = conv['question']
                line += f'[Round {i}]\n问：{user}\n'
                returned.append(line+'答：')

            partial_qas.append({
                'id': id,
                'title': title,
                'description': description,
                'QA_pairs': deepcopy(convs[:i+1]) # a list
            })

            line += '答：{}\n'.format(conv['solution']) 
        return returned, partial_qas