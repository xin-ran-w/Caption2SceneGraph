T2I_2M_DIR=/home/diaomuxi/dataset_zoo/sana_data/T2I-2M
SA_1B_DIR=/home/diaomuxi/dataset_zoo/sana_data/SA-1B

python batch_inference.py \
    --data_dirs $T2I_2M_DIR $SA_1B_DIR \
    --resume