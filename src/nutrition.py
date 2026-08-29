import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("USDA_API_KEY")

# Rough daily targets for an average adult (simplified, not medical advice)
DAILY_TARGETS = {
    "protein": 50,     # grams
    "fiber": 28,       # grams
}

def get_nutrition_for_ingredient(ingredient_name):
    """
    Looks up basic nutrition info for a single ingredient using USDA's API.
    Returns a dict with protein and fiber per 100g, or None if not found.
    """
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "query": ingredient_name,
        "pageSize": 1,
        "api_key": API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get("foods"):
            return None

        food = data["foods"][0]
        nutrients = {n["nutrientName"]: n["value"] for n in food.get("foodNutrients", [])}

        return {
            "name": ingredient_name,
            "protein": nutrients.get("Protein", 0),
            "fiber": nutrients.get("Fiber, total dietary", 0),
        }
    except Exception as e:
        print(f"Nutrition lookup failed for '{ingredient_name}': {e}")
        return None


def estimate_recipe_nutrition(ingredients_list):
    """
    Sums up rough nutrition estimates across a recipe's ingredients.
    """
    total_protein = 0
    total_fiber = 0

    for ingredient in ingredients_list:
        info = get_nutrition_for_ingredient(ingredient)
        if info:
            total_protein += info["protein"]
            total_fiber += info["fiber"]

    return {"protein": round(total_protein, 1), "fiber": round(total_fiber, 1)}


def suggest_nutrition_boost(recipe_nutrition):
    """
    Compares recipe nutrition to daily targets and suggests a simple boost.
    """
    suggestions = []

    if recipe_nutrition["protein"] < DAILY_TARGETS["protein"] * 0.3:
        suggestions.append("Add a boiled egg or a handful of lentils for extra protein.")

    if recipe_nutrition["fiber"] < DAILY_TARGETS["fiber"] * 0.2:
        suggestions.append("Add a side of leafy greens or beans for extra fiber.")

    if not suggestions:
        return "This recipe already contributes well to your daily nutrition!"

    return " ".join(suggestions)


if __name__ == "__main__":
    test_ingredients = ["chicken", "rice", "garlic"]
    nutrition = estimate_recipe_nutrition(test_ingredients)
    print("Estimated nutrition:", nutrition)
    print("Suggestion:", suggest_nutrition_boost(nutrition))
    