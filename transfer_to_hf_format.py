import os
import os.path as osp
import json

from datasets import Dataset
from utils import load_json, load_token


data_dir = "data/Text2SG-deepseek-1k"
tokens = load_token()

def main():
    data_dicts = []
    files = os.listdir(data_dir)
    for f in files:
        try:
            data_dicts.append(load_json(osp.join(data_dir, f)))
        except:
            print(f"The file {f} has error, please check")
            exit()     
    
    descriptions = [data['input'] for data in data_dicts]
    outputs = [json.dumps(data['output']) for data in data_dicts]
    
    hf_ds = Dataset.from_dict({"input": descriptions, "output": outputs})
    hf_ds.push_to_hub("Xinran0906/Text2SG", token=tokens['HF_TOKEN'])
    

if __name__ == "__main__":
    main()
