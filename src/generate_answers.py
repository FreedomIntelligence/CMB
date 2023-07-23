import torch
from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM, AutoModel
import re
import argparse
from accelerate import Accelerator
import json
import random
from tqdm import tqdm
from torch.utils.data import DataLoader
import torch.distributed as dist
from collections import defaultdict

from utils_cgm import LLMZooRunner
from utils_v2 import match_choice, extract_ans, make_output_dir, get_runner_class





def main(args):
    few_shot_prompt = args.few_shot_prompt

    make_output_dir(args.output_path)

    print(few_shot_prompt)


    # todo: wrap everything in runner.run()?
    runner_class = get_runner_class(args.model_id) # raise an error if no mapped class

    from omegaconf import OmegaConf

    config = OmegaConf.load(args.model_config_path)[args.model_id]

    runner = runner_class.from_config(
        config,
        args.input_path,
        args.output_path,
        args.batch_size, # todo: make it nicer
        args.qa_flag, 
        args.cot_flag,
    )

    dataloader_iterator = (
        tqdm(runner.dataloader, total=len(runner.dataloader))
        if runner.accelerator.is_main_process
        else runner.dataloader
    )

    accumulated_response, accumulated_data = [], []
    gathered_idx = set()
    for batch_idx, batch in enumerate(dataloader_iterator, start=1):
        
        # one step to get outputs
        response, data = runner.generate_batch(batch, return_raw=True) 
        accumulated_response.extend(response) # model responses
        accumulated_data.extend(data) # raw data

        # gather data
        if batch_idx % args.all_gather_freq == 0 or batch_idx == len(runner.dataloader):

            all_data = [None] * dist.get_world_size() 
            all_response = [None] * dist.get_world_size() 

            dist.all_gather_object(all_response, accumulated_response)
            dist.all_gather_object(all_data, accumulated_data)


            all_data = [item for sublist in all_data for item in sublist]
            all_response = [item for sublist in all_response for item in sublist]


            # update raw data with model responses
            if args.qa_flag:
                for d, r in zip(all_data, all_response):
                    for idx, _r in enumerate(r):
                        d['QA_pairs'][-1][f"model_answer_{idx}"] = _r
                if runner.accelerator.is_main_process:
                    json.dump(all_data, runner.writer, ensure_ascii=False, indent=4)
            else:
                for d, r in zip(all_data, all_response):
                    if d['id'] in gathered_idx:
                        continue
                    gathered_idx.add(d['id'])
                    for idx, _r in enumerate(r):
                        d[f"answer_{idx}"] = _r
                    if runner.accelerator.is_main_process:
                        runner.writer.write(json.dumps(d, ensure_ascii=False) + "\n")
                        runner.writer.flush()

            if runner.accelerator.is_main_process:
                print(all_response[-1])
                print(f'currently {len(all_response)} items are gathered')
                print("total number of gathered samples", len(gathered_idx))
            accumulated_response, accumulated_data = [], []
    
    runner.close()

    if runner.accelerator.is_main_process:
        if not args.qa_flag:
            print(
                "The answer generation has been completed, and the answer extraction starts below."
            )
            extract_ans(runner.generation_config.num_return_sequences, args.output_path, args.cot_flag)
            print("The answer extraction is complete.")
        else:
            print(f'output to {runner.output_pth}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_id",
        type=str,
        help="model id configured in mode_config_path",
        default="/mntcephfs/data/med/zhanghongbo/MOSS/ckpts/newhuatuo_180K_choice_warmup/latest_tfmr",
    )

    parser.add_argument(
        "--model_config_path",
        type=str,
        help="path to the model configuration file",
        default="/mntcephfs/data/med/xidong/CMB/configs/model_config.yaml"
    )
    parser.add_argument(
        "--input_path",
        type=str,
        help="path to the input data",
    )
    parser.add_argument(
        "--output_path",
        type=str,
        help="path to the output data",
    )
    parser.add_argument(
        "--all_gather_freq",
        type=int,
        default=1,
        help="increase this number to reduce the cost of communication.",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=1,
        help="batch size",
    )
    parser.add_argument(
        "--few_shot_prompt", type=str, help="few shot prompt", default=""
    )
    parser.add_argument(
        "--cot_flag",
        action="store_true",
        help="whether to use cot(action: True)",
    )
    parser.add_argument(
        "--qa_flag",
        action="store_true",
        help="whether to use qa(action: True)",
    )
    parser.add_argument(
        "--use_fewshot",
        action="store_true",
        help="whether to use fewshot(action: True)",
    )
    args = parser.parse_args()

    main(args)


