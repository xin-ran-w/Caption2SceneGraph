import json
import os
import os.path as osp
import argparse

from tqdm import tqdm
from functools import partial
from openai import OpenAI
from concurrent.futures import ProcessPoolExecutor, as_completed

from prompts.scene_graph_parsing import SCENE_GRAPH_PARSING_PROMPT
from prompts.json_schema import JSON_SCHEMA
from utils import save_json, load_json



SYSTEM_PROPMT = SCENE_GRAPH_PARSING_PROMPT.format(examples="")

client = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")

model = "Text2SG-Qwen2.5-3B-Instruct"

def parse_scene_graph(text_data, save_dir):

    # Create client inside the worker process
    filename, text = text_data
    
    try:
        response = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f'{SYSTEM_PROPMT}\nInput: {text}'
            }],
            model=model,
            extra_body={"guided_json": JSON_SCHEMA}
        )
        
        scene_graph = json.loads(response.choices[0].message.content)
        save_json(osp.join(save_dir, filename), {"input": text, "output": scene_graph})
        
    except json.JSONDecodeError:

        print(f"JSON Parsing Error for {filename}.")
        print(response.choices[0].message.content)
    

def main(filenames, texts, save_dir, num_processes=8):
    
    # Prepare data for multiprocessing
    text_data = list(zip(filenames, texts))
    
    # Create partial function with fixed arguments - remove client and model
    process_func = partial(parse_scene_graph, save_dir=save_dir)
    
    # Create process pool and map the function with progress bar
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        futures = {executor.submit(process_func, data): data for data in text_data}

        with tqdm(total=len(text_data), desc="Parsing scene graphs") as pbar:
            for future in as_completed(futures):
                pbar.update(1)
    

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Parse scene graphs from text data.")
    parser.add_argument(
        '--data_dirs', 
        nargs='+', 
        required=True, 
        help='List of directories containing the data files.'
    )

    parser.add_argument(
        '--resume', 
        action='store_true', 
        help='Resume processing from where it left off.'
    )

    args = parser.parse_args()

    data_dirs = args.data_dirs

    for data_dir in data_dirs:
        
        if args.resume:
            save_dir = f"{data_dir}-SG"
            
            if not osp.exists(save_dir):
                os.mkdir(save_dir)
    
            all_files = os.listdir(data_dir)
            exclude_files = os.listdir(save_dir) + ['meta_data.json']
            target_files = list(set(all_files).difference(set(exclude_files)))
        else:
            target_files = [f for f in os.listdir(data_dir) if f != 'meta_data.json']

        captions = []

        for filename in target_files:
            model_name = filename.split('_')[-1].split('.')[0]
            key = '_'.join(filename.split('_')[:-1])
            caption = load_json(osp.join(data_dir, filename))[key][model_name]
            captions.append(caption)
        
        
        print(f'Parsing texts in {data_dir} ......')
        # Run async function
        main(target_files, captions, save_dir=save_dir, num_processes=8)
    