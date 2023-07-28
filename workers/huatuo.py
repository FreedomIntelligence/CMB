
from workers.base import *






class HuatuoWorker(BaseWorker):

    def load_model_and_tokenizer(self, load_config):
        hf_model_config = {"pretrained_model_name_or_path": load_config['config_dir'],'trust_remote_code': True, 'low_cpu_mem_usage': True}
        hf_tokenizer_config = {"pretrained_model_name_or_path": load_config['config_dir'], 'padding_side': 'left', 'trust_remote_code': True}
        precision = load_config.get('precision', 'fp16')
        device = load_config.get('device', 'cuda')
        assert device == "cuda", 'only supports CUDA inference'

        if precision == 'fp16':
            hf_model_config.update({"torch_dtype": torch.float16})

        tokenizer = AutoTokenizer.from_pretrained(**hf_tokenizer_config)
        model = AutoModelForCausalLM.from_pretrained(**hf_model_config)
        model.eval()
        return model, tokenizer
    @property
    def system_prompt(self):
        return "一位用户和智能医疗大模型HuatuoGPT之间的对话。对于用户的医疗问诊，HuatuoGPT给出准确的、详细的、温暖的指导建议。对于用户的指令问题，HuatuoGPT给出有益的、详细的、有礼貌的回答。"
    @property
    def instruction_template(self,):
        return self.system_prompt + '<病人>：{instruction} <HuatuoGPT>：'
    @property
    def instruction_template_with_fewshot(self,):
        return self.system_prompt + '{fewshot_examples}<病人>：{instruction} <HuatuoGPT>：'
    @property
    def fewshot_template(self, eos='</s>'):
        return "<病人>：{user} <HuatuoGPT>：{gpt}" + eos
    
    def collate_conv(self, data, eos='</s>'):
        returned = [] # this is fed into the model for outputs
        partial_qas = []
        line = self.system_prompt
        
        id = data['id']
        title = data['title']
        description = data['description']
        convs = data['QA_pairs']

        for i, conv in enumerate(convs):
            if i == 0:
                line += '<病人>：{}{} '.format(description, conv['question']) # a space after the patients' input
            else:
                line += '<病人>：{} '.format(conv['question']) # a space after the patients' input
            returned.append(line + '<HuatuoGPT>：') 

            partial_qas.append({
                'id': id,
                'title': title,
                'description': description,
                'QA_pairs': deepcopy(convs[:i+1]) # a list
            })

            line += '<HuatuoGPT>：{}'.format(conv['solution']) + eos
        return returned, partial_qas
    
    



if __name__ == '__main__':
    worker = HuatuoWorker()
    n = 10000
    items = [{
        "exam_type": "专业知识考试",
        "exam_class": "中医学与中药学",
        "exam_subject": "中医学",
        "question": "肝主疏泄，主要表现在",
        "answer": "BCDE",
        "explanation": "肝主疏泄的表现：肝的疏泄功能反映了肝为刚脏，主升主动的生理特点，是调畅全身气机，推动血和津液运行的重要环节。表现在以下三方面。一是调畅气机：气机是气的升降出入运动。机体的脏腑、经络、器官等的活动，全赖气的升降出入运动。肝的生理功能特点是主升主动，这对于气机的疏通、畅达和升发，医|学教育网整理是一个重要的因素。因此，肝的疏泄功能是否正常，对于气的升降出入之间的平衡协调，起着调节作用。肝的疏泄功能正常，则气机调畅，气血和调，经络通利，脏腑器官等的活动也就正常和调。若肝的疏泄功能失常，则一肝的疏泄功能减退，可见气的升发不足，气机的疏通和畅达受阻，从而形成气机不畅、气机郁结等病理变化；二是肝的升发太过，则气的升发过亢，气的下降不及，从而形成肝气上逆的病理变化。甚则气升太过，血随气逆，出现吐血、咯血等表现。甚或突然昏不知人。（大怒则形气绝，而血菀于上，使人薄厥）。二是促进脾胃运化功能：肝的疏泄功能正常，是脾胃正常升降的一个重要条件。肝的疏泄功能失常，不仅可影响脾的升清功能，在上则为眩晕，在下则为餮泄；还能影响胃的降浊功能，在上则为呕逆嗳气，在中则为脘胀疼痛，在下则为便秘。肝的疏泄功能有助于脾胃运化功能还体现于胆汁的分泌与排泄。胆与肝相连，胆汁为肝之余气积聚而成。胆汁的分泌与排泄实际上是肝主疏泄功能的一个方面。肝的疏泄功能正常，则胆汁能正常分泌和排泄，有助于脾胃的运化功能。三调畅情志：情志活动属于心主神明的功能，但亦与肝的疏泄功能密切相关。因为正常的情志活动主要依赖于气血的正常运行，情志异常对机体生理活动的重要影响也在于干扰正常的气血运行。所以，肝的疏泄功能具有调畅情志的作用，实际上是调畅气机功能的派生的。此外，妇女的月经和排卵、男子的排精等与肝的疏泄功能也有密切关系。",
        "question_type": "多项选择题",
        "option": {
            "A": "通调水道",
            "B": "调畅气机",
            "C": "助脾运化",
            "D": "条达情志",
            "E": "调节生殖功能"
        }}]*n
    
    import time
    tic = time.perf_counter()
    example1 = worker.generate_fewshot_examples(items, use_cot=True)
    toc = time.perf_counter()
    print(f"{n} items are processed in {toc - tic:0.4f} seconds")
    # example2 = worker.collate_fewshot(items, use_cot=False)
    # print('-'*10 + 'cot' + '-'*10)
    # print(example1)
    # print('-'*10 + 'no cot' + '-'*10)
    # print(example2)
