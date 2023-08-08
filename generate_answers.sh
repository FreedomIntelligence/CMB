input_path='./data/CMB-Exam/CMB-test/CMB-test-choice-question-merge.json'   # CMB-Exam
# input_path='./data/CMB-Clin/CMB-Clin-qa.json'                             # CMB-Clin



task_name='Exam' 

model_id="huatuo-chat" # which model to evaluate
mkdir -p logs/${task_name}/

accelerate launch --main_process_port 27274 --config_file ./configs/accelerate_config.yaml  ./src/generate_answers.py \
--use_cot \
--model_id=$model_id \
--all_gather_freq=20 \
--input_path=$input_path \
--output_path=./result/${task_name}/${model_id}/modelans.json \
--batch_size 1 \
--model_config_path="./configs/model_config.yaml" 