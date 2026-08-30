import os
import base64
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def recognize_ingredients_from_photo(image_path):
    base64_image = encode_image(image_path)

    response = client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Look at this photo of groceries/ingredients. "
                            "List ONLY the food ingredients you can clearly identify, "
                            "as a simple comma-separated list (e.g., 'chicken, garlic, rice'). "
                            "Do not describe the image, do not add explanations, just the list."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        temperature=0.2,
    )

    raw_output = response.choices[0].message.content.strip()

    # Strip out any <think>...</think> reasoning block the model includes
    cleaned_output = re.sub(r"<think>.*?</think>", "", raw_output, flags=re.DOTALL).strip()

    return cleaned_output


if __name__ == "__main__":
    result = recognize_ingredients_from_photo("data/test_groceries.jpg")
    print("Recognized ingredients:")
    print(result)