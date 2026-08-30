# Rough average prices in INR per common unit, for demonstration purposes.
# In a production system, this would come from a live grocery API or regularly updated dataset.
INGREDIENT_PRICE_TABLE = {
    "chicken": 200,       # per 500g
    "rice": 60,           # per kg
    "garlic": 20,         # per 100g
    "onion": 30,          # per kg
    "egg": 6,             # per piece
    "milk": 30,           # per 500ml
    "cheese": 100,        # per 200g
    "butter": 50,         # per 100g
    "tomato": 40,         # per kg
    "potato": 25,         # per kg
    "shrimp": 400,        # per 250g
    "beef": 350,          # per 500g
    "pasta": 80,          # per 500g
    "flour": 45,          # per kg
    "sugar": 45,          # per kg
    "salt": 20,           # per kg
    # Add more as needed — this is intentionally a starting reference set
}

DEFAULT_UNKNOWN_PRICE = 30  # fallback estimate for ingredients not in the table


def estimate_recipe_cost(ingredients_list):
    """
    Rough total cost estimate for a recipe based on its ingredient list.
    This is an approximation using average per-unit prices, not live pricing.
    """
    total_cost = 0
    breakdown = {}

    for ingredient in ingredients_list:
        ingredient_lower = ingredient.lower().strip()
        matched_price = None

        # Check for partial matches (e.g., "chicken breasts" should match "chicken")
        for known_ingredient, price in INGREDIENT_PRICE_TABLE.items():
            if known_ingredient in ingredient_lower:
                matched_price = price
                break

        if matched_price is None:
            matched_price = DEFAULT_UNKNOWN_PRICE

        breakdown[ingredient] = matched_price
        total_cost += matched_price

    return {"total_estimated_cost_inr": total_cost, "breakdown": breakdown}


def is_within_budget(recipe_cost, user_budget):
    """Simple check: does the estimated recipe cost fit within the stated budget?"""
    return recipe_cost["total_estimated_cost_inr"] <= user_budget


if __name__ == "__main__":
    test_ingredients = ["chicken", "rice", "garlic", "onion"]
    cost = estimate_recipe_cost(test_ingredients)
    print("Cost estimate:", cost)
    print("Within ₹300 budget?", is_within_budget(cost, 300))