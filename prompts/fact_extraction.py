FACT_EXTRACTION_PROMPT = """You are an AI assistant and your task is to removing all non-visual information in a description, leaving only the visual facts in a coherent descriptive sentence. Visual facts include details that can be observed (such as colors, shapes, sizes, textures, spatial relationships, and physical features). Remove any speculative, subjective, or non-visual details. Don't change the content of the visual facts part! If all description content is the visual facts, just return the original description.

Example:

Input:
A sleek vehicle with black multi-spoke rims, and red brake calipers, likely belonging to an enthusiast or a dealership.
Output:
A sleek vehicle with black multi-spoke rims, and red brake calipers.

"""