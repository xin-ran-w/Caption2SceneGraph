import json
from openai import OpenAI
from pprint import pprint
from prompts.scene_graph_parsing import SCENE_GRAPH_PARSING_PROMPT
from prompts.json_schema import JSON_SCHEMA

SYSTEM_PROPMT = SCENE_GRAPH_PARSING_PROMPT.format(examples="")

client = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")

models = client.models.list()
model = models.data[0].id


from pydantic import BaseModel
from enum import Enum


def parse_scene_graph(text):
    # Create client inside the worker process
    model = "Text2SG-Qwen2.5-3B-Instruct"
    
    response = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": f'{SYSTEM_PROPMT}\nInput: {text}'
        }],
        model=model,
        extra_body={"guided_json": JSON_SCHEMA}
    )
    
    scene_graph = json.loads(response.choices[0].message.content)
    print(scene_graph)


if __name__ == "__main__":

    text = "A close-up of a white mannequin head wearing a pair of dangling earrings with a star-shaped design and a small diamond-like stone at the center."

    text = "A muscular man is wearing red boxing gloves and blue shorts."
    parse_scene_graph(text)


