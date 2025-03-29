import json

def load_json(file):
    with open(file) as f:
        return json.load(f)

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)


def convert_json_to_jinja(input_json, output_jinja):
    # Input and output file paths
    json_file_path = "Text2SG-gemma-3-4b-it/chat_template.json"
    jinja_file_path = "Text2SG-gemma-3-4b-it/chat_template.jinja"
    
    try:
        # Read the JSON file
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            template_data = json.load(json_file)
        
        # Extract the chat template
        template_content = template_data['chat_template']
        
        # Write to Jinja file
        with open(jinja_file_path, 'w', encoding='utf-8') as jinja_file:
            # The template content is already in Jinja format, 
            # we just need to unescape the newlines and quotes
            template_content = template_content.replace('\\n', '\n')
            template_content = template_content.replace('\\"', '"')
            jinja_file.write(template_content)
            
        print(f"Successfully converted {json_file_path} to {jinja_file_path}")
        
    except FileNotFoundError:
        print("Error: Input file not found")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format")
    except KeyError:
        print("Error: 'chat_template' key not found in JSON")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def load_token():
    return load_json("configs/tokens.json")


if __name__ == "__main__":
    pass
