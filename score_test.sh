
model_id="chatmed-consult"
task="Zero-test-cot"
modelans_path=/mntcephfs/data/med/xidong/CMB/result/${task}/${model_id}/modelans.json
groundtruth_path='/mntcephfs/data/med/xidong/CMB/data/ground_truth/CMB-test-choice-answer.json' # 不变
result_path=/mntcephfs/data/med/xidong/CMB/result/${task}/${model_id}/check.json
score_path=/mntcephfs/data/med/xidong/CMB/result/${task}/${model_id}/score.json
python ./src/score_test.py \
--modelans_path=${modelans_path} \
--groundtruth_path=${groundtruth_path} \
--result_path=${result_path} \
--score_path=${score_path}

echo "output to $score_path"