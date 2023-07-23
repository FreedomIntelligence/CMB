test_data='/mntcephfs/data/med/xidong/CMB/data/CMB-main/CMB-test/CMB-test-choice-question-merge.json' #不变
# test_data='/mntcephfs/data/med/xidong/CMB/data/CMB-test-qa/CMB-test-qa.json' #不变



task_name='Zero-test-cot'

model_id="huatuo"
# cot
nohup accelerate launch --gpu_ids='all' --main_process_port 27274 --config_file ./configs/accelerate_config.yaml  ./src/generate_answers.py \
--model_id=$model_id \
--all_gather_freq=20 \
--input_path=$test_data \
--output_path=/mntcephfs/data/med/xidong/CMB/result/${task_name}/${model_id}/modelans.json \
--cot_flag \ 
--model_config_path="./configs/model_config.yaml" > ./logs/${task_name}/${model_id}.log 2>&1 &

