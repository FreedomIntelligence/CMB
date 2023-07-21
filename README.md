# CMB Chinese-Medical-Benchmark 
<p align="center">
   🌐 <a href="" target="_blank">Website</a> • 🤗 <a href="" target="_blank">Hugging Face</a> • 📃 <a href="" target="_blank">Paper</a>  <br>  <a href="">   中文</a> | <a href="">English 
</p>

## 更新

* **[2023.07.23]**  CMB公开！感谢支持~


## 数据下载
- 方法一：直接下载使用[zip压缩文件]()
- 方法二：使用[Hugging Face datasets]()直接加载数据集 示例如下:
  ```python
  from datasets import load_dataset
  
  # main datasets （multiple choice）
  main_datasets = load_dataset('FreedomIntelligence/CMB','main')
  # exam paper datasets （multiple choice）
  exam_datasets = load_dataset('FreedomIntelligence/CMB','exampaper')
  # QA datasets
  qa_datasets = load_dataset('FreedomIntelligence/CMB','qa')
  ```
## 排行榜
我们在初始版本中进行评估的模型的zero-shot和five-shot准确率，请访问我们[官方排行榜]()了解详细结果。


## 数据集介绍
### 组成部分
- CMB-main  
   - CMB-test: CMB医疗模型能力测评数据集———11200道题目
      - 数据量: 6大项28小项，详见[目录](catalog.md), 每一个小项400道题;
      - 评价依据：准确率排名;
      - 目的：多方位测评模型能力;
  - CMB-val: CMB Few-shot数据——280道详细解析题目
      - 数据量：每个小项有10道，共280道;
      - 目的：Few Shot;
   - CMB-train: CMB训练数据集——304743道题目
      - 数据量：6大项28小项，详见[目录](catalog.md);
      - 目的：模型医疗知识注入;
- CME-test-qa: CMB真实病例诊断能力测评数据集———73个教科书级详细病例以及诊断
   - 数据量: 73个详细教科书级病例 以及诊断问题;
   - 评价依据：专业医生人工评价;
   - 目的：评价模型是否具有临床问诊能力;
- CMB-test-exampaper: CMB真题测评数据集——7051道题目
   - 数据量：9小项，26套题目，详见[真题目录](exam-catalog.md);
   - 评价依据：模型是否通过考试(60分);
   - 目的：评测模型是否可以部署使用;


### 目录结构 [目录](catalog.md)
- 大项分类依据：不同的临床工种，和特殊考试 (详见[目录](catalog.md)) [医学考研题目] [学科知识点考察题目]
- 小项分类依据：不同的医学相关职业等级(详见[目录](catalog.md)) [部分区分了中西医] 
- 完整题目汇总为 xxxx-merge.json ; 目录结构为 xxxx-hierarchy.json

### CMB-Test & Train & Exampaper Item 
```json
{
    "exam_type": "医师考试",
    "exam_class": "执业医师",
    "exam_subject": "口腔执业医师",
    "question": "患者，男性，11岁。近2个月来时有低热（37～38℃），全身无明显症状。查体无明显阳性体征。X线检查发现右肺中部有一直径约0.8cm类圆形病灶，边缘稍模糊，肺门淋巴结肿大。此男孩可能患",
    "answer": "D",
    "question_type": "单项选择题",
    "option": {
        "A": "小叶型肺炎",
        "B": "浸润性肺结核",
        "C": "继发性肺结核",
        "D": "原发性肺结核",
        "E": "粟粒型肺结核"
    }
},
```
- exam_type: 大项分类; 不同的临床工种，和特殊考试 (详见[目录](catalog.md)) [医学考研题目] [学科知识点考察题目];
- exam_class: 小项分类; 不同的医学相关职业等级(详见[目录](catalog.md)) [部分区分了中西医];
- exam_subject: 具体科室或细分学科分类; 
- question_type: 只有"单项选择题"和"多项选择题";

### CMB-qa Item 
```json
{
    "id": "0",
    "title": "案例分析-腹外疝",
    "description": "现病史\n（1）病史摘要\n     病人，男，49岁，3小时前解大便后出现右下腹疼痛，右下腹可触及一包块，既往体健。\n（2）主诉\n     右下腹痛并自扪及包块3小时。\n\n体格检查\n体温： T 37.8℃，P 101次／分，呼吸22次/分，BP 100/60mmHg，腹软，未见胃肠型蠕动波，肝脾肋下未及，于右侧腹股沟区可扪及一圆形肿块，约4cm×4cm大小，有压痛、界欠清，且肿块位于腹股沟韧带上内方。\n\n辅助检查\n（1）实验室检查\n     血常规：WBC 5.0×109／L，N 78％。\n     尿常规正常。\n（2）多普勒超声检查\n     沿腹股沟纵切可见一多层分布的混合回声区，宽窄不等，远端膨大，边界整齐，长约4～5cm。\n（3）腹部X线检查\n     可见阶梯状液气平。",
    "QA_pairs": [
        {
            "question": "简述该病人的诊断及诊断依据。",
            "answer": "诊断：嵌顿性腹股沟斜疝合并肠梗阻。\n      诊断依据：\n      ①右下腹痛并自扪及包块3小时；\n      ②有腹胀、呕吐，类似肠梗阻表现；腹部平片可见阶梯状液平，考虑肠梗阻可能；腹部B超考虑， \n腹部包块内可能为肠管可能；\n      ③有轻度毒性反应或是中毒反应，如 T 37.8℃，P 101次／分，白细胞中性分类78％；\n      ④腹股沟区包块位于腹股沟韧带上内方。"
        },
        {
            "question": "简述该病人的鉴别诊断。",
            "answer": "（1）睾丸鞘膜积液：鞘膜积液所呈现的肿块完全局限在阴囊内，其上界可以清楚地摸到；用透光试验检查肿块，鞘膜积液多为透光（阳性），而疝块则不能透光。\n     （2）交通性鞘膜积液：肿块的外形与睾丸鞘膜积液相似。于每日起床后或站立活动时肿块缓慢地出现并增大。平卧或睡觉后肿块逐渐缩小，挤压肿块，其体积也可逐渐缩小。透光试验为阳性。\n     （3）精索鞘膜积液：肿块较小，在腹股沟管内，牵拉同侧睾丸可见肿块移动。\n     （4）隐睾：腹股沟管内下降不全的睾丸可被误诊为斜疝或精索鞘膜积液。隐睾肿块较小，挤压时可出现特有的胀痛感觉。如患侧阴囊内睾丸缺如，则诊断更为明确。\n     （5）急性肠梗阻：肠管被嵌顿的疝可伴发急性肠梗阻，但不应仅满足于肠梗阻的诊断而忽略疝的存在；尤其是病人比较肥胖或疝块较小时，更易发生这类问题而导致治疗上的错误。\n     （6）此外，腹股沟区肿块还应与以下疾病鉴别:肿大的淋巴结、动（静）脉瘤、软组织肿瘤、脓肿、\n圆韧带囊肿、子宫内膜异位症等。"
        },
        {
            "question": "简述该病人的治疗原则。",
            "answer": "嵌顿性疝原则上需要紧急手术治疗，以防止疝内容物坏死并解除伴发的肠梗阻。术前应做好必要的准备，如有脱水和电解质紊乱，应迅速补液加以纠正。手术的关键在于正确判断疝内容物的活力，然后根据病情确定处理方法。在扩张或切开疝环、解除疝环压迫的前提下，凡肠管呈紫黑色，失去光泽和弹性，刺激后无蠕动和相应肠系膜内无动脉搏动者，即可判定为肠坏死。如肠管尚未坏死，则可将其送回腹腔，按一般易复性疝处理，即行疝囊高位结扎+疝修补术。如肠管确已坏死或一时不能肯定肠管是否已失去活力时，则应在病人全身情况允许的前提下，切除该段肠管并进行一期吻合。凡施行肠切除吻合术的病人，因手术区污染，在高位结扎疝囊后，一般不宜作疝修补术，以免因感染而致修补失败。"
        }
    ]
}
```
- title: 病例疾病名称;
- description: 病例信息;
- QA_pairs: 一系列诊断问题和对应标准回答;





## 如何进行评测和提交

### 修改模型配置文件
`configs/model_config.yaml` 示例如下：
```
my_model:
    model_id: 'my_model'
    system_template: "病人：{instruction}\n医生：" # system prompt，可为空字符串；如非空，则必须带有 `{instruction}` 的placeholder
    load:
        # HuggingFace模型权重文件夹
        config_dir: "path/to/full/model"

        # 使用peft加载LoRA模型
        # llama_dir: "path/to/base"
        # lora_dir: "path/to/lora"

        device: 'cuda'          # 当前仅支持cuda
        precision: 'fp16'       # 推理精度，支持 fp16, fp32

    # inference解码超参,支持 transformers.GenerationConfig 的所有参数
    generation_config: 
        max_new_tokens: 512     
        min_new_tokens: 1          
        do_sample: False         

    # inference batch_size
    batch_size: 2
```


### 添加模型加载代码
Step 1: 在 `ModelLoader` 类中**添加**如下函数：
```
class ModelLoader():
    def load_my_model_and_tokenizer(self):
        config = self.config
        model_id = self.model_id
        assert config.get(model_id), f'{model_id} is not configured in configs/model_config.yaml'
        load_config = config.get(model_id).load


        # 根据需要修改
        hf_model_config = {
            "pretrained_model_name_or_path": load_config['config_dir'], 
            'trust_remote_code': True, 
            'low_cpu_mem_usage': True
        }
        hf_tokenizer_config = {
            "pretrained_model_name_or_path": load_config['config_dir'], 
            'padding_side': 'left', 
            'trust_remote_code': True
        }
        model = AutoModelForCausalLM.from_pretrained(**hf_model_config).half()
        tokenizer = AutoTokenizer.from_pretrained(**hf_tokenizer_config)
        # model = PeftModel.from_pretrained(model, load_config['lora_dir'], torch_dtype=torch.float16)

        # 返回 model 和 tokenizer，注意模型需要在cpu上
        return model, tokenizer
```

Step 2: 在 `LLMZooRunner.init_model_and_tokenizer()` 中，将
```
self.model, self.tokenizer, config = model_loader.load_model_and_tokenizer()
```
替换为
```
self.model, self.tokenizer, config = model_loader.load_my_model_and_tokenizer()
```



### 修改运行配置文件
`generate_answers.sh` 示例如下：

```
# # 输入文件路径
# test_data_path='./data/CMB-main/CMB-test/CMB-test-choice-question-merge.json'   # 医疗模型能力测评数据集
# test_data_path='./data/CMB-test-exampaper/CMB-test-exam-merge.json'             # 真题测评数据集
# test_data_path='./data/CMB-test-qa/CMB-test-qa.json'                            # 真实病例诊断能力测评数据集


task_name='Zero-test-cot'   
port_id=27272

model_id="my_model"                                                      # 模型id，应与`./configs/model_config.yaml` 中添加的model_id保持一致

accelerate launch \
    --gpu_ids='all' \                                                   # 使用所有可用GPU
    --main_process_port $port_id \                                      # 端口
    --config_file ./configs/accelerate_config.yaml  \                   # accelerate 配置文件路径
    ./src/generate_answers.py \                                         # 主程序
    --model_id=$model_id \                                              # 模型ID
    --cot_flag \                                                        # 是否使用CoT prompt模板                                   
    --input_path=$test_data_path \                                      # 输入文件路径
    --output_path=./result/${task_name}/${model_id}/answers.json \      # 输出文件路径
    --model_config_path="./configs/model_config.yaml"                   # 模型配置文件路径
```


### 开始评测

Step 1: 生成回答 + 抽取答案
```
bash generate_answers.sh
```

Step 2: 计算得分
```
bash score_exam.sh # 医疗模型能力测评数据集
bash score_test.sh # 真题测评数据集
```

### 提交结果
将 [开始评测](###开始评测) 中 **Step 1** 在**测试集**的输出文件提交至xxx，我们将在第一时间更新排行榜。


## CMB评测细节

### CMB Test & Train & Exampaper Prompt
CMB-test Item [样例]()
#### Answer-only Prompt
```
{System_prompt}

<{Role_1}>：以下是中国{exam_type}中{exam_class}考试的一道{question_type}，不需要做任何分析和解释，直接输出答案选项。。
{题目}
A. {选项A}
B. {选项B}
...
<{Role_2}>：A

[n-shot demo, n is 0 for the zero-shot case]

<{Role_1}>：以下是中国{exam_type}中{exam_class}考试的一道{question_type}，不需要做任何分析和解释，直接输出答案选项。
{题目}
A. {选项A}
B. {选项B}
...
<{Role_2}>：
```
#### Chain-of-thought Prompt

```
{System_prompt}

<{Role_1}>：以下是中国{exam_type}中{exam_class}考试的一道{question_type}，请分析每个选项，并最后给出答案。
{题目}
A. {选项A}
B. {选项B}
...
<{Role_2}>：.......所以答案是A

[n-shot demo, n is 0 for the zero-shot case]

<{Role_1}>：以下是中国{exam_type}中{exam_class}考试的一道{question_type}，请分析每个选项，并最后给出答案。
{题目}
A. {选项A}
B. {选项B}
...
<{Role_2}>：
```

### CMB-qa Prompt
CMB-test-qa Item [样例]()
```
{System_prompt}

<{Role_1}>：以下是一位病人的病例：
{description}
{QA_pairs[0]['question']}
<{Role_2}>：..........
[n-question based on the len(QA_pairs)]
```


## 许可证




## 引用

如果您使用我们的数据集，请引用我们的论文。
```

```
