import os
import json
import random

from openai import OpenAI
from pprint import pprint

from prompts.reference_expression_generation import REFERENCE_EXPRESSION_GENERATION_PROMPT
from prompts.scene_graph_parsing import SCENE_GRAPH_PARSING_PROMPT
from prompts.fact_extraction import FACT_EXTRACTION_PROMPT

from utils import load_json


api_key = "sk-90066e5902634884b73c3c071cda5ab5"
ds_client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
model = "deepseek-chat"



EXAMPLES = [load_json(os.path.join("data/text-to-image-2M-new", f)) for f in os.listdir("data/text-to-image-2M-new")]



def extract_visual_facts(description):
    
    visual_facts = ds_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": FACT_EXTRACTION_PROMPT},
            {"role": "user", "content": f"Now, please process the following description by dropping any non-visual facts:\nDescription: {description}. \nPlease directly return the results."}
        ],
    )

    return visual_facts.choices[0].message.content


def parse_description_to_scene_graph(description):
    
    examples = random.sample(EXAMPLES, 3)
    few_shot_prompt = [f"EXAMPLE INPUT\n{e['input']}\nEXAMPLE JSON OUTPUT\n{json.dumps(e['output'])}" for e in examples]
    
    messages = [
        {"role": "system", "content": SCENE_GRAPH_PARSING_PROMPT.format(examples=few_shot_prompt)},
        {"role": "user", "content": f"INPUT\n {description}. \nPlease directly return the results."}
    ]

    response = ds_client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={'type': 'json_object'}
    )

    messages.append(response.choices[0].message)

    scene_graph_dict = json.loads(response.choices[0].message.content)
    pprint(scene_graph_dict)
    
    
    # scene_graph_dict = format_checking(scene_graph_dict, messages, correct=correct)

    return scene_graph_dict

def generate_reference_expression(scene_graph_dict, description):
    
    ref_exps = []

    id2instance = {}

    for instance in scene_graph_dict['instances']:
        instance_id = instance['id']
        instance_category = instance['category']
        id2instance[instance_id] = instance_category
    
    for instance in scene_graph_dict['instances']:
        instance_id = instance['id']
        instance_category = instance['category']
        
        instance_attributes = []
        instance_relations = []

        for attribute_triplet in scene_graph_dict['attributes']:
            if attribute_triplet['instance_id'] == instance_id:
                if isinstance(attribute_triplet["value"], list):
                    for value in attribute_triplet["value"]:
                        instance_attributes.append(
                            f"{attribute_triplet['attribute']}: {value}"
                        )
                else:
                    instance_attributes.append(
                        f"{attribute_triplet['attribute']}: {attribute_triplet['value']}"
                    )

        
        
        for rel_triplet in scene_graph_dict['relations']:
            if rel_triplet['source'] == instance_id:
                target_id = rel_triplet["target"]
                instance_relations.append(
                    f"{instance_category}, {rel_triplet['relation']}, {id2instance[target_id]}"
                )
    
        instance_attributes = "\n".join(instance_attributes)
        instance_relations = "\n".join(instance_relations)
        
        instance_context = f"Attributes:\n{instance_attributes}\n\nRelations:\n{instance_relations}\n\nDescription:{description}"

        messages = [
            {"role": "system", "content": REFERENCE_EXPRESSION_GENERATION_PROMPT},
            {"role": "user", "content": f"Generate the referenece expression of this instance: {instance_category}. Here is the context: {instance_context}\nPlease directly return the referenece expression."}
        ]

        response = ds_client.chat.completions.create(
            model=model,
            messages=messages
        )

        ref_exps.append(response.choices[0].message.content) 

    return ref_exps
        




    
def main():

    description = "A bottle of Tormore Single Malt Whisky with a green label and a cork stopper. The bottle is placed in front of a box with a picture of a mountainous landscape and a river. The label reads 'TORMORE' and 'SINGLE MALT WHISKY' with the age '12 YEARS' and 'AGED IN OAK CASKS'. The bottle has a dark amber color with a gradient towards the top, and the label has a black and white design with the number '1780' in the center."
    
    scene_graph = parse_description_to_scene_graph(description)

    pprint(scene_graph)


if __name__ == "__main__":
    main()


