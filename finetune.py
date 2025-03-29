from unsloth import FastLanguageModel, is_bfloat16_supported
from unsloth.chat_templates import get_chat_template, train_on_responses_only

import json

from transformers import TextStreamer
from datasets import load_dataset
from trl import SFTTrainer, SFTConfig
from pprint import pprint

from prompts.scene_graph_parsing import SCENE_GRAPH_PARSING_PROMPT


SYSTEM_PROPMT = SCENE_GRAPH_PARSING_PROMPT.format(examples="")



def main():

    max_seq_length = 8192 # Choose any! We auto support RoPE Scaling internally!
    dtype = None # None for auto detection. Float16 for Tesla T4, V100, Bfloat16 for Ampere+
    load_in_4bit = False # Use 4bit quantization to reduce memory usage. Can be False.



    model, tokenizer = FastLanguageModel.from_pretrained(
    # Can select any from the below:
    # "unsloth/Qwen2.5-0.5B", "unsloth/Qwen2.5-1.5B", "unsloth/Qwen2.5-3B"
    # "unsloth/Qwen2.5-14B",  "unsloth/Qwen2.5-32B",  "unsloth/Qwen2.5-72B",
    # And also all Instruct versions and Math. Coding verisons!
        model_name = "/home/diaomuxi/model_zoo/Qwen2.5-3B-Instruct",
        max_seq_length = max_seq_length,
        dtype = dtype,
        load_in_4bit = load_in_4bit,
        # token = "hf_...", # use one if using gated models like meta-llama/Llama-2-7b-hf
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r = 16, # Choose any number > 0 ! Suggested 8, 16, 32, 64, 128
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj",],
        lora_alpha = 16,
        lora_dropout = 0, # Supports any, but = 0 is optimized
        bias = "none",    # Supports any, but = "none" is optimized
        # [NEW] "unsloth" uses 30% less VRAM, fits 2x larger batch sizes!
        use_gradient_checkpointing = "unsloth", # True or "unsloth" for very long context
        random_state = 3407,
        use_rslora = False,  # We support rank stabilized LoRA
        loftq_config = None, # And LoftQ
    )


    def apply_chat_template(examples):
        texts = []
        for input_text, output_text in zip(examples['input'], examples['output']):
            texts.append(
                tokenizer.apply_chat_template(
                    [
                        { 'role': 'user', 'content': f'{SYSTEM_PROPMT}\nInput: {input_text}' },
                        { 'role': 'assistant', 'content': output_text }
                    ], 
                    tokenize=False
                )
            )
        return {"text" : texts}
    
    dataset = load_dataset("Xinran0906/Text2SG", split = "train")
    dataset = dataset.map(apply_chat_template, batched = True, keep_in_memory=True)

    print("Training data example: ")
    print(dataset[0]["text"])

    trainer = SFTTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = dataset,
        eval_dataset = None, # Can set up evaluation!
        args = SFTConfig(
            dataset_text_field = "text",
            per_device_train_batch_size = 8,
            gradient_accumulation_steps = 1, # Use GA to mimic batch size!
            warmup_steps = 10,
            # num_train_epochs = 1, # Set this for 1 full training run.
            max_steps = 150,
            learning_rate = 2e-4, # Reduce to 2e-5 for long training runs
            logging_steps = 1,
            optim = "adamw_8bit",
            weight_decay = 0.01,
            lr_scheduler_type = "linear",
            seed = 3407,
            report_to = "none", # Use this for WandB etc
            fp16 = not is_bfloat16_supported(),
            bf16 = is_bfloat16_supported(),
        ),
    )
    
    trainer = train_on_responses_only(
        trainer,
        instruction_part = "<|im_start|>user\n",
        response_part = "<|im_start|>assistant\n",
    )

    trainer.train()

    print("Test Example")

    desp = "A tall man in a blue shirt is sitting on a bench in the park."
    
    messages = [{
        "role": "user",
        "content": f"{SYSTEM_PROPMT}\nInput: {desp}"
    }]
    
    input_text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt = True, # Must add for generation
    )
    model_inputs = tokenizer([input_text], return_tensors="pt").to("cuda")

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens = 4096
    )

    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    generated_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    # Validate JSON
    try:
        scene_graph = json.loads(generated_text)

        # save for vllm
        # save_path = "./Text2SG-Qwen-3B-Instruct-LoRA"
        # print(f"Saving LoRA to {save_path}")
        # model.save_pretrained(save_path)  # Local saving
        # tokenizer.save_pretrained(save_path)

        model.save_pretrained_merged("Text2SG-Qwen2.5-3B-Instruct", tokenizer, save_method = "merged_16bit")

        return scene_graph

        
    except json.JSONDecodeError:

        return {"error": "Generated invalid JSON", "raw_output": generated_text}


if __name__ == "__main__":
    main()
    