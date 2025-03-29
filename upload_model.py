from transformers import AutoModelForCausalLM
from huggingface_hub import HfApi, Repository

from utils import load_token

# Define your model and repository details
model_name = "Text2SG-Qwen2.5-3B-Instruct"
repo_name = "Xinran0906/Text2SG-Qwen2.5-3B-Instruct"

tokens = load_token()
# Load your model (replace with actual model loading code)
model = AutoModelForCausalLM.from_pretrained(model_name)

model.push_to_hub(repo_name, token=tokens['HF_TOKEN'])

if __name__ == "__main__":
    pass