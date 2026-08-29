import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_recipe_response(query, results, df, guardrail_message):
    """
    Takes the user's query, the retrieved recipe indices, and the guardrail message,
    and asks the LLM to write a natural response grounded ONLY in these recipes.
    """
    if not results:
        return "I couldn't find any recipes matching your request in our database."

    # Build a clean text block of the actual retrieved recipes
    recipe_context = ""
    for idx in results:
        title = df.iloc[idx]["title"]
        ingredients = df.iloc[idx]["ingredients_text"]
        recipe_context += f"- {title}: {ingredients}\n"

    prompt = f"""You are a helpful cooking assistant. A user asked: "{query}"

Here are the ONLY recipes you are allowed to recommend, retrieved from our database:
{recipe_context}

Guardrail note: {guardrail_message}

Instructions:
- Recommend ONE recipe from the list above that best fits the user's request.
- Briefly explain why it fits.
- If the guardrail note indicates a weak match, honestly tell the user their exact ingredients weren't a perfect match, and mention this clearly.
- Do NOT invent any recipe, ingredient, or detail not listed above.
- Keep your response to 3-4 sentences.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,  # lower temperature = more consistent, less "creative" drift
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    # Quick manual test using fake data
    import pickle
    with open("data/recipe_embeddings.pkl", "rb") as f:
        data = pickle.load(f)
    df = data["df"]

    fake_results = df[df["ingredients_text"].str.contains("chicken", case=False)].index[:3].tolist()
    fake_guardrail_msg = "✅ These results are a strong match for your ingredients."

    output = generate_recipe_response("chicken, rice, garlic", fake_results, df, fake_guardrail_msg)
    print(output)