from openai import OpenAI 
import base64

MODEL="gpt-4o-mini"
KEY = "GPT_KEY"
client = OpenAI(api_key=KEY)

def encode_image(image: bytes):
    return base64.b64encode(image).decode("utf-8")

def generate_recipe_from_img(image: bytes, type: str | None) -> str:
    base64_image = encode_image(image)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": f"You are an experienced cook chief that responds in Markdown in russian language. You tell nothing but only recipes. Help me cook dish using ingredients from fridge from provided image! At the end include nutrition information about 100g of final product." + (f"Recipe will be for {type} dish" or "")},
            {"role": "user", "content": [
                {"type": "text", "text": "What can be cooked with these ingredients from fridge on provided image below?"},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"}
                }
            ]}
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content
