import re
# Category expansions — map common exclusion terms to what they actually cover
EXCLUSION_EXPANSIONS = {
    "shellfish": ["shrimp", "crab", "oyster", "oysters", "clam", "clams", "lobster", "scallop", "scallops"],
    "nuts": ["peanut", "peanuts", "almond", "almonds", "cashew", "cashews", "walnut", "walnuts",
             "pecan", "pecans", "pistachio", "pistachios", "hazelnut", "hazelnuts"],
    "dairy": ["milk", "cheese", "cream", "butter", "yogurt"],
    "eggs": ["egg"],
    "soy": ["soy sauce", "tofu", "edamame"],
}

def expand_exclusions(exclusion_list):
    """
    Takes raw excluded words and expands categories into their actual ingredients.
    e.g. 'shellfish' -> ['shellfish', 'shrimp', 'crab', 'oyster', ...]
    """
    expanded = set()
    for word in exclusion_list:
        expanded.add(word)
        # Check if this word matches a category (allowing for "-free" stripped already)
        for category, items in EXCLUSION_EXPANSIONS.items():
            if word == category or word in items:
                expanded.add(category)
                expanded.update(items)
    return list(expanded)

def parse_constraints(query):
    """
    Extracts structured constraints from a natural language query.
    Returns a dictionary with whatever fields it could detect.
    """
    query_lower = query.lower()
    constraints = {}

    # --- Time constraint (e.g. "under 20 minutes", "in 15 mins") ---
    time_match = re.search(r"(under|in|within)\s+(\d+)\s*(minutes|mins|min)", query_lower)
    if time_match:
        constraints["max_time_minutes"] = int(time_match.group(2))

    # --- Dietary restrictions ---
    dietary_keywords = ["vegetarian", "vegan", "gluten-free", "dairy-free", "keto"]
    found_dietary = [word for word in dietary_keywords if word in query_lower]
    if found_dietary:
        constraints["dietary"] = found_dietary

       # --- Allergy / exclusions (e.g. "no nuts", "without dairy", "shellfish-free") ---
    exclusion_match = re.findall(r"(?:no|without|allergic to)\s+(\w+)", query_lower)
    free_match = re.findall(r"(\w+)-free", query_lower)  # catches "shellfish-free", "nut-free"
    
    all_exclusions = exclusion_match + free_match
    if all_exclusions:
        constraints["exclude"] = expand_exclusions(all_exclusions)

    # --- Spice level ---
    if "spicy" in query_lower or "hot" in query_lower:
        constraints["spice_level"] = "spicy"
    elif "mild" in query_lower:
        constraints["spice_level"] = "mild"

        # --- Budget: extract an actual number if given (e.g., "under ₹300", "budget of 200") ---
    budget_match = re.search(r"(?:₹|rs\.?|inr)\s*(\d+)|(\d+)\s*(?:₹|rs\.?|inr)", query_lower)
    if budget_match:
        amount = budget_match.group(1) or budget_match.group(2)
        constraints["max_budget_inr"] = int(amount)
    elif "budget" in query_lower or "cheap" in query_lower or "affordable" in query_lower:
        constraints["budget_conscious"] = True  # signal present, but no specific number given

    # --- Everything else is treated as the ingredient/free-text part ---
    # Strip out the parts we already parsed, roughly, to isolate ingredients
    constraints["raw_query"] = query

    return constraints


# Quick manual tests
if __name__ == "__main__":
    test_queries = [
        "chicken, garlic, rice, spicy, under 20 minutes",
        "vegetarian pasta without nuts, budget-friendly",
        "something mild with shrimp, gluten-free",
    ]
    for q in test_queries:
        print(f"\nQuery: {q}")
        print("Parsed:", parse_constraints(q))