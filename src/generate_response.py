import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_recipe_response(query, results, df, guardrail_message):
    """
    Takes the user's query, the retrieved recipe indices, and the guardrail message,
    and asks the LLM to write a full, grounded, warm recipe response.
    """
    if not results:
        return "I couldn't find any recipes matching your request in our database."

    # Build a clean text block of the actual retrieved recipes, including real directions
    recipe_context = ""
    for idx in results:
        title = df.iloc[idx]["title"]
        ingredients = df.iloc[idx]["ingredients_text"]
        directions = df.iloc[idx].get("directions", "No directions available in dataset.")
        recipe_context += f"\nRecipe: {title}\nIngredients: {ingredients}\nDirections: {directions}\n"

    prompt = f"""You are a warm, friendly cooking assistant. A user asked: "{query}"

Here are the ONLY recipes you are allowed to recommend, retrieved from our database:
{recipe_context}

Guardrail note: {guardrail_message}

Write your response exactly in this format, using this structure and nothing extra:

🍽️ [Recipe Name]

[One warm, conversational opening line recommending this dish. If the guardrail note indicates a weak or partial match, say so honestly right here — e.g. "Heads up, this isn't a perfect match for everything you listed, but it's the closest thing we've got."]

🧂 What you'll need:
- ingredient one
- ingredient two
- ingredient three

👩‍🍳 How to make it:
1. First step
2. Second step
3. Third step

[One short, friendly closing line — mention plainly if any of the user's ingredients weren't used, in a casual way, not a formal "Note:" section.]

Rules:
- Use the ingredients and directions EXACTLY as given above — do not shorten, invent, or skip steps.
- Do NOT use bold text, horizontal rule dividers (---), markdown headers (##), or a formal "Note:" section.
- Do NOT invent any ingredient, step, or detail not listed above.
- Keep the tone casual and warm, like texting a friend a recipe — not a technical report.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    import pickle
    with open("data/recipe_embeddings.pkl", "rb") as f:
        data = pickle.load(f)
    df = data["df"]

    fake_results = df[df["ingredients_text"].str.contains("chicken", case=False)].index[:3].tolist()
    fake_guardrail_msg = "✅ These results are a strong match for your ingredients."

    output = generate_recipe_response("chicken, rice, garlic", fake_results, df, fake_guardrail_msg)
    print(output)