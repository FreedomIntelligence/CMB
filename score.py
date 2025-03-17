import json

# 读取CMB-test-choice-answer (3).json文件
with open('/data/ground_truth/CMB-test-choice-answer.json', 'r', encoding='utf-8') as f:
    cmb_data = json.load(f)

#  读取model_answer_demo.json文件
with open('model_answer.json', 'r', encoding='utf-8') as f:
    model_data = json.load(f)

# 将WiseDiag数据转换为字典，方便查找
wisediag_dict = {item['id']: item['model_answer'] for item in model_data}

# 初始化统计字典
accuracy_stats = {}

# 遍历CMB数据，进行对比和统计
for item in cmb_data:
    exam_type = item['exam_type']
    exam_class = item['exam_class']
    question_id = item['id']
    correct_answer = item['answer']
    model_answer = wisediag_dict.get(question_id, '')

    # 初始化统计结构
    if exam_type not in accuracy_stats:
        accuracy_stats[exam_type] = {}
    if exam_class not in accuracy_stats[exam_type]:
        accuracy_stats[exam_type][exam_class] = {'correct': 0, 'total': 0}

    # 统计正确和总数
    accuracy_stats[exam_type][exam_class]['total'] += 1
    if correct_answer == model_answer:
        accuracy_stats[exam_type][exam_class]['correct'] += 1

# 计算准确率并保存到结果字典
result = {
    "accuracy_per_category": {},
    "accuracy_per_subcategory": {}
}

# 计算每个 exam_type 的平均分
for exam_type, classes in accuracy_stats.items():
    total_accuracy = 0  # 用于计算当前 exam_type 的平均分
    class_count = 0  # 用于计算当前 exam_type 的平均分

    # 初始化子类别准确率字典
    result["accuracy_per_subcategory"][exam_type] = {}

    for exam_class, stats in classes.items():
        accuracy = stats['correct'] / stats['total']  # 计算准确率（小数形式）
        result["accuracy_per_subcategory"][exam_type][exam_class] = accuracy
        total_accuracy += accuracy
        class_count += 1

    # 计算当前 exam_type 的平均分
    average_accuracy = total_accuracy / class_count if class_count > 0 else 0
    result["accuracy_per_category"][exam_type] = average_accuracy

# 将结果保存到JSON文件
with open('accuracy_results_structured.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)

print("结构化准确率统计结果已保存到 accuracy_results_structured.json 文件中。")
