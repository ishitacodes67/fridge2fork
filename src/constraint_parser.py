import re

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

    # --- Allergy / exclusions (e.g. "no nuts", "without dairy") ---
    exclusion_match = re.findall(r"(?:no|without|allergic to)\s+(\w+)", query_lower)
    if exclusion_match:
        constraints["exclude"] = exclusion_match

    # --- Spice level ---
    if "spicy" in query_lower or "hot" in query_lower:
        constraints["spice_level"] = "spicy"
    elif "mild" in query_lower:
        constraints["spice_level"] = "mild"

    # --- Budget signal (very rough for now) ---
    if "budget" in query_lower or "cheap" in query_lower or "affordable" in query_lower:
        constraints["budget_conscious"] = True

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