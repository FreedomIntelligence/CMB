import argparse
import json
import random
import os

from constants import id2worker_class
from tqdm import tqdm
import pdb


query_prompt_1 = "以下是中国{exam_type}中{exam_class}考试的一道{question_type}，请分析每个选项，并最后给出答案。\n{question}\n{option_str}"
query_prompt_2 = "以下是中国{exam_type}中{exam_class}考试的一道{question_type}，不需要做任何分析和解释，直接输出答案选项。\n{question}\n{option_str}"

data_val = []

def get_output_path(args):
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir, exist_ok=True)
    
    cot_or_a = 'cot' if args.use_cot else 'a'
    f_name = f'CMB-Exam-{cot_or_a}-{args.model_id}.json'
    output_path = os.path.join(args.output_dir, f_name)
    return output_path

def select_items(exam_type, exam_class, num):
        # Filter the data based on the given exam_type and exam_class
    filtered_data = [
        item
        for item in data_val
        if item["exam_type"] == exam_type and item["exam_class"] == exam_class
    ]
    # Check if we have enough items
    if len(filtered_data) < num:
        raise ValueError(f"Not enough items matching the given criteria: {exam_type}, {exam_class}")

    # Select a random sample of items
    selected_items = random.sample(filtered_data, num)

    return selected_items


def get_query(da, use_cot):
    da["option_str"] = "\n".join(
        [f"{k}. {v}" for k, v in da["option"].items() if len(v) > 0 and v!=" "]
    )
    if use_cot:
        query = query_prompt_1.format_map(da)
    else:
        query = query_prompt_2.format_map(da)

    return query


def main(args):
    output_path = get_output_path(args)
    with open(args.test_path, "r", encoding="utf-8") as f:
        data_test = json.load(f)

    # initialize a worker
    from omegaconf import OmegaConf

    worker = id2worker_class[args.model_id].from_config(
        OmegaConf.load(args.model_config_path)[
            args.model_id
        ],
        generate_fewshot_examples_only=True,
    )
    for item in tqdm(data_test):
        # select examples
        samples = select_items(
            item["exam_type"], item["exam_class"], args.n_shot
        )
        # one step to generate formatted few-shot examples
        item["fewshot_examples"] = worker.generate_fewshot_examples(
            data=samples, use_cot=args.use_cot
        )

    directory = os.path.dirname(output_path)
    
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(data_test, output_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_shot", type=int, help="number of shots", default=5)
    parser.add_argument(
        "--model_config_path",
        type=str,
        help="path to the model configuration file",
        default='configs/model_config.yaml'
    )
    parser.add_argument(
        "--model_id",
        type=str,
        help="model id",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        help="path to the val json",
    )
    parser.add_argument(
        "--val_path",
        type=str,
        help="path of the val file",
    )
    parser.add_argument(
        "--test_path",
        type=str,
        help="path of the test file",
    )
    parser.add_argument(
        "--use_cot",
        action="store_true",
        help="whether to use cot(action: True)",
    )

    args = parser.parse_args()

    

    with open(args.val_path, "r", encoding="utf-8") as f:
        data_val = json.load(f)
    main(args)

