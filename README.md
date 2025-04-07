# Caption2SceneGraph
A parser tool using large language model to parse the input caption into a scene graph

## Overview
Caption2SceneGraph is a tool that converts natural language image descriptions into structured scene graphs using Large Language Models (LLMs). It extracts visual elements, relationships, and attributes from textual descriptions to create a comprehensive scene representation.

## Features
- Visual fact extraction from captions
- Scene graph parsing with entity recognition
- Attribute and relationship extraction

## Installation

```bash
git clone https://github.com/yourusername/Caption2SceneGraph
cd Caption2SceneGraph
pip install -r requirements.txt
```

## Finetuning Dataset

We collect 1k parser results from the deepseek-chat API. We upload the input text and output scene graph paired dataset here: [Xinran0906/Text2SG](https://huggingface.co/datasets/Xinran0906/Text2SG). You can use this dataset to train your own parser.


