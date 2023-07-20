# CMB Chinese-Medical-Benchamrk 
<p align="center">
   🌐 <a href="" target="_blank">Website</a> • 🤗 <a href="" target="_blank">Hugging Face</a> • 📃 <a href="" target="_blank">Paper</a>  <br>  <a href="">   中文</a> | <a href="">English 
</p>

## News

* **[2023.07.23]**  CMB Chinese-Medical-Benchmark 放出！感谢支持~


## 数据下载
- 方法一：直接下载使用[zip压缩文件]()
- 方法二：使用[Hugging Face datasets]()直接加载数据集 示例如下:
  ```python
  ```
## 排行榜
我们在初始版本中进行评估的模型的zero-shot和five-shot准确率，请访问我们[官方排行榜]()了解详细结果。


## 数据集介绍
### 组成部分
- CMB-test: CMB医疗模型能力测评数据集(11200道题目)
   - 数据量: 6大项28小项，每一个小项400道题;
   - 评价依据：准确率排名;
   - 目的：多方位测评模型能力;
- CME-test-qa: CMB真实病例诊断能力测评数据集(73个教科书病例)
   - 数据量: 73个详细教科书级病例 以及诊断问题;
   - 评价依据：专业医生人工评价;
   - 目的：评价模型是否具有临床问诊能力;
- CMB-test-zhenti: CMB真题测评数据集(7051道题目)
   - 数据量：3大项9小项，26套题目;
   - 评价依据：模型是否通过考试(60分);
   - 目的：评测模型是否可以部署使用;
- CMB-val: CMB Few-shot数据(附带详细解析)
   - 数据量：每个小项有10道，共280道;
   - 目的：Few Shot;
- CMB-train: CMB训练数据集(304743道题)
   - 数据量：6大项28小项，详见/CMB-train/CMB-train-hierarchy.json;
   - 目的：模型医疗知识注入;

### 目录结构
- 大项分类依据：不同的临床工种，和特殊考试 [医学考研题目] [学科知识点考察题目]
- 小项分类依据：不同的医学相关职业等级(详见[等级目录](catalog.md)) [部分区分了中西医] 
- 完整题目汇总为 xxxx-merge.json ; 目录结构为 xxxx-hierarchy.json

### CMB-Test & Train & Zhenti Item 
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
- exam_type: 大项分类; 不同的临床工种，和特殊考试 [医学考研题目] [学科知识点考察题目];
- exam_class: 小项分类; 不同的医学相关职业等级(详见[等级目录](catalog.md)) [部分区分了中西医];
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
            "answer": "......"
        },
        {
            "question": "简述该病人的治疗原则。",
            "answer": "....."
        }
    ]
}
```
- title: 病例疾病名称;
- description: 病例信息;
- QA_pairs: 一系列诊断问题和对应标准回答;



## 如何进行评测和提交


## CMB评测细节

### CMB Test & Train & Zhenti Prompt
CMB-test Item [Sample description]()
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

{System_prompt}
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

{System_prompt}
<{Role_1}>：以下是中国{exam_type}中{exam_class}考试的一道{question_type}，请分析每个选项，并最后给出答案。
{题目}
A. {选项A}
B. {选项B}
...
<{Role_2}>：
```

### CMB-qa Prompt
CMB-test-qa item [Sample description]()
```
{System_prompt}
<{Role_1}>：以下是一位病人的病例：
{description}
{QA_pairs[0]['question']}
<{Role_2}>：..........
[n-question based on the len(QA_pairs)]
```


## 许可证




## 感谢您的引用和支持

Please cite our paper if you use our dataset.
```

```
