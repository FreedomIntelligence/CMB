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

from utils_v2 import match_choice, extract_ans, make_output_dir, get_runner_class

import os
import pdb

def get_fewshot_input_path(args):
    assert (args.test and not args.exam) or (args.exam and not args.test)
    print('using fewshot inputs. Ignoring args.input_path...')
    exam_or_test = 'exam' if args.exam else 'test'
    cot_or_a = 'cot' if args.use_cot else 'a'
    inp_pth = os.path.join('data', f'fewshot-CMB-{exam_or_test}-{cot_or_a}', f'CMB-test-{args.model_id}-merge.json')
    assert os.path.isfile(inp_pth), f'file {inp_pth} has not been generated.'
    print(f'loading fewshot examples from {inp_pth}')

    return inp_pth


def main(args):

    make_output_dir(args.output_path)
    if args.use_fewshot:
        if args.use_input_path:
            print(f'use_input_path=True. Loading data from {args.input_path}')
            pass
        else:
            args.input_path = get_fewshot_input_path(args)


    # todo: wrap everything in runner.run()?
    runner_class = get_runner_class(args.model_id) # raise an error if no mapped class

    from omegaconf import OmegaConf

    config = OmegaConf.load(args.model_config_path)[args.model_id]

    runner = runner_class.from_config(
        config,
        args.input_path,
        args.output_path,
        args.batch_size, # todo: make it nicer
        use_qa = args.use_qa, 
        use_cot = args.use_cot,
        use_fewshot = args.use_fewshot,
    )

    
    dataloader_iterator = (
        tqdm(runner.dataloader, total=len(runner.dataloader))
        if runner.accelerator.is_main_process
        else runner.dataloader
    )
    past_data = []
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
            new_all_data, new_all_response = [], []
            if args.use_qa:
                to_be_updated = set()
                for d, r in zip(all_data, all_response):
                    if d['id'] in gathered_idx:
                        continue
                    for idx, _r in enumerate(r):
                        d['QA_pairs'][-1][f"model_answer_{idx}"] = _r
                    new_all_data.append(d)
                    new_all_response.append(r)
                    to_be_updated.add(d['id'])

                    if runner.accelerator.is_main_process:
                        runner.writer.write(json.dumps(d, ensure_ascii=False) + "\n")
                        runner.writer.flush()

                gathered_idx.update(to_be_updated)
                past_data.extend(new_all_data)
            else:
                for d, r in zip(all_data, all_response):
                    # if args.test:
                    if d['id'] in gathered_idx:
                        continue
                    gathered_idx.add(d['id'])

                    for idx, _r in enumerate(r):
                        d[f"answer_{idx}"] = _r
                    if runner.accelerator.is_main_process:
                        runner.writer.write(json.dumps(d, ensure_ascii=False) + "\n")
                        runner.writer.flush()
                    new_all_data.append(d)
                    new_all_response.append(r)

            if runner.accelerator.is_main_process:
                if batch_idx == 0:
                    print('QUERY:', d['query'])
                print(all_response[-1])
                print(f'currently {len(new_all_response)} items are gathered')
                print("total number of gathered samples", len(gathered_idx))
            accumulated_response, accumulated_data = [], []
    
    runner.close()

    if runner.accelerator.is_main_process:
        if not args.use_qa:
            print(
                "The answer generation has been completed, and the answer extraction starts below."
            )
            extract_ans(runner.generation_config.num_return_sequences, args.output_path, args.use_cot)
            print("The answer extraction is complete.")
        else:
            lines = []
            with open(runner.output_pth, 'r') as f:
                for line in f:
                    lines.append(json.loads(line))
            with open(runner.output_pth, 'w') as f:
                json.dump(lines, f, ensure_ascii=False, indent=4)
            
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
        default=3,
        help="batch size",
    )
    parser.add_argument(
        "--use_cot",
        action="store_true",
        help="whether to use cot(action: True)",
    )
    parser.add_argument(
        "--use_qa",
        action="store_true",
        help="whether to use qa(action: True)",
    )
    parser.add_argument(
        "--use_fewshot",
        action="store_true",
        help="whether to use fewshot(action: True)",
    )
    parser.add_argument(
        "--use_input_path",
        action="store_true",
        help="whether to use input_path(action: True)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="whether to use fewshot(action: True)",
    )
    parser.add_argument(
        "--exam",
        action="store_true",
        help="whether to use fewshot(action: True)",
    )

    
    args = parser.parse_args()

    main(args)


