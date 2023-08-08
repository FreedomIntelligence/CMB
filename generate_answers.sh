test_data='./data/CMB-Exam/CMB-test/CMB-test-choice-question-merge.json' # 
# test_data='./data/CMB-Clin/CMB-Clin-qa.json' #不变



task_name='Exam'

model_id="huatuo-chat"
mkdir -p logs/${task_name}/

accelerate launch --main_process_port 27274 --config_file ./configs/accelerate_config.yaml  ./src/generate_answers.py \
--model_id=$model_id \
--all_gather_freq=20 \
--input_path=$test_data \
--output_path=./result/${task_name}/${model_id}/modelans.json \
--use_cot \
--batch_size 1 \
--model_config_path="./configs/model_config.yaml" 