# vllm serve /home/diaomuxi/model_zoo/Qwen2.5-3B-Instruct \
#     --max-model-len 4096 \
#     --enable-lora \
#     --lora-modules text2sg-lora=./Text2SG-Qwen-3B-Instruct \
#     --tensor-parallel-size 1


vllm serve Text2SG-Qwen2.5-3B-Instruct --tensor-parallel-size 1