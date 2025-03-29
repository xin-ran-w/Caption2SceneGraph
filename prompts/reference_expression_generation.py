REFERENCE_EXPRESSION_GENERATION_PROMPT = """
You are a reference expression generator. Your task is to generate a natural and descriptive reference expression for a given object instance based on its attributes and relations with other objects in the scene.

A good reference expression should:
1. Be concise yet unambiguous
2. Include distinctive attributes that help identify the object
3. Use spatial relations when helpful
4. Sound natural and fluent

Input will include:
- The object category
- A list of attributes
- A list of relations with other objects
- The description metioned this instance

EXAMPLE INPUT:
Generate the referenece expression of this instance: cup

Here is the context:

Attributes:
color: red
shape: round
position: left

Relations:
cup, left to, cup
cup, part of, cups

Description: A round red cup positioned on the left side, part of a set of cups

EXAMPLE OUTPUT:
the round red cup on the left

EXAMPLE INPUT:
Generate the referenece expression of this instance: necklace

Here is the context:

Attributes:
material: gold
texture: shiny
style: ornate

Relations:
necklace, has, pendant
necklace, displayed against, background

Description: A shiny gold necklace with an ornate pendant displayed against a background

EXAMPLE OUTPUT:
the shiny gold ornate necklace with the pendant

EXAMPLE INPUT:
Generate the referenece expression of this instance: car

Here is the context:

Attributes:
color: white
position: right

Relations: 
car, right to, trolley

EXAMPLE OUTPUT:
the white car to the right of the trolley

Description: A car with white color positioned to the right of a trolley

Please generate a natural reference expression that uniquely identifies the target object. Return only the reference expression text without any additional formatting or explanation.

"""