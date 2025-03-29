import os
import networkx as nx
import gradio as gr

from pyvis.network import Network
from parser import parse_description_to_scene_graph
from utils import load_json, save_json


def load_text_to_image_2M():
    data_dir = "/mnt/sdc/huggingface/dataset_hub/text-to-image-2M/data_1024_10K"
    prompt_json_list = [file for file in os.listdir(data_dir) if file.endswith(".json") and file not in os.listdir("data/text-to-image-2M")]
    prompts = [(file, load_json(os.path.join(data_dir, file))['prompt']) for file in prompt_json_list]
    return prompts

prompts = iter(load_text_to_image_2M())

def create_graph_from_triplets(triplets):
    G = nx.DiGraph()
    for triplet in triplets:
        subject, predicate, obj = triplet
        G.add_edge(str(subject).strip(), str(obj).strip(), label=str(predicate).strip())
    return G


def get_node_color(node):

    if node == 'meta_image.n1':
        return 'pink'
    elif '.n' in node:        
        return 'skyblue'
    else:
        return 'orange'


def nx_to_pyvis(networkx_graph):
    pyvis_graph = Network(notebook=True, cdn_resources='remote', directed=True)
    for node in networkx_graph.nodes():
        pyvis_graph.add_node(node, color=get_node_color(node))
    for edge in networkx_graph.edges(data=True):
        pyvis_graph.add_edge(edge[0], edge[1], label=edge[2]["label"])
    return pyvis_graph


def transfer_scene_graph_dict_to_triplets(scene_graph_dict):
    
    triplets = []
    # process entities

    instances = scene_graph_dict['instances']

    for a_triplet in scene_graph_dict['attributes']:
        
        if isinstance(a_triplet['id'], list): 
            for instance in a_triplet['id']:
                if instance in instances:
                    if isinstance(a_triplet['value'], list):
                        for value in a_triplet['value']:
                            triplets.append([instance, a_triplet['dimension'], value])
                    else:
                        triplets.append([instance, a_triplet['dimension'], a_triplet['value']])
        else:
            instance = a_triplet['id']
            if instance in instances:
                if isinstance(a_triplet['value'], list):
                    for value in a_triplet['value']:
                        triplets.append([instance, a_triplet['dimension'], value])
                else:
                    triplets.append([instance, a_triplet['dimension'], a_triplet['value']])

    for r_triplet in scene_graph_dict['relations']:
        
        relation = r_triplet.get('relation')
        
        if relation is not None:
            
            source = r_triplet['source']
            target = r_triplet['target']
    
            if isinstance(source, list): 
                for s in source:
                    if s in instances:
                        if isinstance(target, list):
                            for t in target:
                                if t in instances:
                                    triplets.append([source, relation, t])
                        else:
                            if target in instances:
                                triplets.append([source, relation, target])

            else:
                if source in instances:
                    if isinstance(target, list):
                        for t in target:
                            if t in instances:
                                triplets.append([source, relation, t])
                    else:
                        if target in instances:
                            triplets.append([source, relation, target])
    return triplets


def parse_scene_graph(description):

    scene_graph = parse_description_to_scene_graph(description)

    triplets = transfer_scene_graph_dict_to_triplets(scene_graph)

    graph = create_graph_from_triplets(triplets)
    pyvis_network = nx_to_pyvis(graph)

    pyvis_network.toggle_hide_edges_on_drag(True)
    pyvis_network.toggle_physics(False)
    pyvis_network.set_edge_smooth('discrete')

    html = pyvis_network.generate_html()
    html = html.replace("'", "\"")

    return f"""<iframe style="width: 100%; height: 600px;margin:0 auto" name="result" allow="midi; geolocation; microphone; camera;
    display-capture; encrypted-media;" sandbox="allow-modals allow-forms
    allow-scripts allow-same-origin allow-popups
    allow-top-navigation-by-user-activation allow-downloads" allowfullscreen=""
    allowpaymentrequest="" frameborder="0" srcdoc='{html}'></iframe>""", scene_graph


def save_scene_graph(description, file_name, json_str):
    save_path = os.path.join("data/text-to-image-2M", file_name)
    data = {
        "input": description,
        "output": json_str
    }
    save_json(save_path, data)
    print(f"Saving scene graph to {save_path}")


if __name__ == "__main__":
    
    with gr.Blocks(title='Cap2SG') as demo:

        file_name = gr.State('')

        with gr.Column():
            output_html = gr.HTML()
            with gr.Row():
                input_text = gr.TextArea(max_lines=20)
                output_json = gr.JSON()
            with gr.Row():
                clear = gr.ClearButton()
                clear.add([output_html, input_text, output_json])
                parse_button = gr.Button(value='parse')
                save_button = gr.Button(value='save')
                next_button = gr.Button(value='next')
        
        next_button.click(
            lambda: next(prompts),
            inputs=[],
            outputs=[file_name, input_text]
        )
        
        parse_button.click(
            parse_scene_graph, 
            inputs=[input_text],
            outputs=[output_html, output_json]
        )

        save_button.click(
            save_scene_graph,
            inputs=[input_text, file_name, output_json], 
        )

        demo.launch(server_name="10.160.4.190", server_port=8081)
