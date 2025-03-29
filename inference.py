import json
import os
import os.path as osp

from tqdm import tqdm
from multiprocessing import Pool
from functools import partial
from openai import OpenAI

from prompts.scene_graph_parsing import SCENE_GRAPH_PARSING_PROMPT
from utils import save_json, load_json



SYSTEM_PROPMT = SCENE_GRAPH_PARSING_PROMPT.format(examples="")

client = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")

models = client.models.list()
model = models.data[0].id

def parse_single_scene_graph(text_data, save_dir):
    # Create client inside the worker process
    model = "Text2SG-Qwen2.5-3B-Instruct"
    filename, text = text_data
    
    try:
        response = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f'{SYSTEM_PROPMT}\nInput: {text}'
            }],
            model=model,
        )
        
        scene_graph = json.loads(response.choices[0].message.content)
        save_json(osp.join(save_dir, filename), scene_graph)
        
    except json.JSONDecodeError:
        print(f"JSON Parsing Error for {filename}.")
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        # Optionally, return an error message or code
        return f"Error: {e}"



def parse_scene_graph(filenames, texts, save_dir, num_processes=8):
    
    if not osp.exists(save_dir):
        os.mkdir(save_dir)
    
    # Prepare data for multiprocessing
    text_data = list(zip(filenames, texts))
    
    # Create partial function with fixed arguments - remove client and model
    process_func = partial(parse_single_scene_graph, save_dir=save_dir)
    
    # Create process pool and map the function with progress bar
    with Pool(processes=num_processes) as pool:
        list(tqdm(
            pool.imap(process_func, text_data),
            total=len(text_data),
            desc="Parsing scene graphs"
        ))
    


if __name__ == "__main__":
    
    data_dirs = [
        "/home/diaomuxi/dataset_zoo/sana_data/T2I-2M"
    ]

    caption_file_lists = [] 
    captions = []

    for data_dir in data_dirs:

        file_list = os.listdir(data_dir)
        file_list = [f for f in file_list if f != 'meta_data.json']
        caption_file_lists.extend(file_list)
        
        captions.extend(
            [
                load_json(osp.join(data_dir, file))['_'.join(file.split('_')[:-1])]
                for file in file_list
            ]
        )

    # Run async function
    parse_scene_graph(caption_file_lists, captions, save_dir="/home/diaomuxi/dataset_zoo/sana_data/T2I-2M-SG", num_processes=64)
    