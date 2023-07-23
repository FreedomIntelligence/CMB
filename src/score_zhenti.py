import argparse
import json
from collections import defaultdict

def calculate_accuracy(all_dict, right_dict):
    accuracy_dict = defaultdict(int)
    for key in all_dict:
        if key in right_dict:
            accuracy_dict[key] = right_dict[key] / all_dict[key]
        else:
            accuracy_dict[key] = 0  # 如果right_dict中没有这个key，那么准确率为0
    return accuracy_dict

def calculate_class_accuracy(all_subject_dict, right_class_dict):
    accuracy_class_dict = defaultdict(lambda: defaultdict(int))
    for key in all_subject_dict:
        accuracy_class_dict[key] = calculate_accuracy(all_subject_dict[key], right_class_dict[key])
    return accuracy_class_dict

def calculate_class_type_accuracy(all_subject_type_dict, right_class_type_dict):
    accuracy_class_type_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for key in all_subject_type_dict:
        for inner_key in all_subject_type_dict[key]:
            accuracy_class_type_dict[key][inner_key] = calculate_accuracy(all_subject_type_dict[key][inner_key], right_class_type_dict[key][inner_key])
    return accuracy_class_type_dict



def scorer(args):
    with open(args.modelans_path, "r", encoding='utf-8') as file:
        modelans = json.load(file)

    all = defaultdict(int)
    all_subject = defaultdict(lambda: defaultdict(int))
    all_subject_type = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    right = defaultdict(int)
    right_class = defaultdict(lambda: defaultdict(int))
    right_class_type = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))


    for item in modelans:
        if 'model_answer' in item:
            exam_class = item['exam_class']
            exam_subject = item['exam_subject']
            question_type = item['question_type']

            if exam_subject == '2023真题':
                continue
            all[exam_class] += 1
            all_subject[exam_class][exam_subject] += 1
            all_subject_type[exam_class][exam_subject][question_type] += 1

            if item['answer'] == item['model_answer']:
                right[exam_class] += 1
                right_class[exam_class][exam_subject] += 1
                right_class_type[exam_class][exam_subject][question_type] += 1

    accuracy_dict = calculate_accuracy(all, right)
    accuracy_subject_dict = calculate_class_accuracy(all_subject, right_class)
    accuracy_subject_type_dict = calculate_class_type_accuracy(all_subject_type, right_class_type)


    accuracy_json = {
        'accuracy': accuracy_dict,
        'accuracy_subject': accuracy_subject_dict,
        'accuracy_subject_type': accuracy_subject_type_dict
    }

    with open(args.score_path, 'w', encoding="utf8") as f:
        json.dump(accuracy_json, f, ensure_ascii=False, indent=4)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--modelans_path",
        type=str,
        help="path to the model ans file",
    )
    parser.add_argument(
        "--score_path",
        type=str,
        help="path to the final score path",
    )
    args = parser.parse_args()
    scorer(args)