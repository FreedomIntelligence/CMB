
model_id="baichuan-13b-chat"
n_shot=3

test_path=data/CMB-Exam/CMB-test/CMB-test-choice-question-merge.json 
val_path=data/CMB-Exam/CMB-val/CMB-val-merge.json
output_dir=data/fewshot
python ./src/generate_fewshot.py \
--use_cot \
--n_shot=$n_shot \
--model_id=$model_id \
--output_dir=$output_dir  \
--val_path=$val_path \
--test_path=$test_path 