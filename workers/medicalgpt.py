
from .base import *





class MedicalGPTWorker(BaseWorker):

    def load_model_and_tokenizer(self, load_config):
        hf_model_config = {"pretrained_model_name_or_path": load_config['config_dir'],'trust_remote_code': True, 'low_cpu_mem_usage': True}
        hf_tokenizer_config = {"pretrained_model_name_or_path": load_config['config_dir'], 'padding_side': 'left', 'trust_remote_code': True}

        device = load_config.get('device', 'cuda')
        precision = load_config.get('precision', 'fp16')

        assert device == "cuda", 'only supports CUDA inference'
        assert precision in ['fp16', 'fp32'], 'Only supports fp16/32 for now'

        if precision == 'fp16':
            hf_model_config.update({"torch_dtype": torch.float16})

        model = AutoModelForCausalLM.from_pretrained(**hf_model_config)
                
        tokenizer = LlamaTokenizer.from_pretrained(**hf_tokenizer_config)

        model.eval()
        return model, tokenizer
    
    @property
    def system_prompt(self):
        return "Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n"
    @property
    def instruction_template(self,):
        return self.system_prompt + '### Instruction:{instruction}\n\n### Response: '
    @property
    def instruction_template_with_fewshot(self,):
        return self.system_prompt + '### Instruction:{fewshot_examples}{instruction}\n\n### Response: '
        # https://huggingface.co/shibing624/ziya-llama-13b-medical-merged
    
    @property
    def fewshot_template(self,):
        return "问题：{user}\n答案：{gpt}\n\n"
    @property
    def fewshot_separator(self,):
        return "\n\n"
    
    def generate_fewshot_examples(self, data: list[dict], use_cot=False):
        """Generate a fewshot prompt given a list of data"""
        prompt = self.fewshot_prompt
        for round, item in enumerate(data):
            user, gpt = self.format_fewshot_user_and_gpt(item, use_cot)
            prompt += self.fewshot_template.format(user=user, gpt=gpt) + self.fewshot_separator
        return prompt

    def collate_conv(self, data,):
        returned = []
        partial_qas = []
        line = self.system_prompt + '### Instruction:'
        
        id = data['id']
        title = data['title']
        description = data['description']
        convs = data['QA_pairs']

        for i, conv in enumerate(convs):
            if i == 0:
                line += '{}问题：{}'.format(description, conv['question']) 
            else:
                line += '问题：{}'.format(conv['question'])
            returned.append(line + '\n\n### Response: ')
            partial_qas.append({
                'id': id,
                'title': title,
                'description': description,
                'QA_pairs': deepcopy(convs[:i+1]) # a list
            })

            line += '答案：{}'.format(conv['solution']) + self.fewshot_separator
        return returned, partial_qas


