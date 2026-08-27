eval_queries = [
    # --- Easy / baseline ---
    {"id": 1, "query": "chicken, rice, garlic", "category": "easy"},
    {"id": 2, "query": "pasta with tomato sauce", "category": "easy"},
    {"id": 3, "query": "eggs and cheese", "category": "easy"},
    {"id": 4, "query": "beef and potatoes", "category": "easy"},
    {"id": 5, "query": "shrimp and rice", "category": "easy"},

    # --- Constraint-heavy ---
    {"id": 6, "query": "vegetarian pasta without nuts, under 20 minutes", "category": "constraint_heavy"},
    {"id": 7, "query": "spicy chicken, gluten-free, budget-friendly", "category": "constraint_heavy"},
    {"id": 8, "query": "mild soup without dairy, under 30 minutes", "category": "constraint_heavy"},
    {"id": 9, "query": "vegan dinner without soy, quick", "category": "constraint_heavy"},
    {"id": 10, "query": "keto breakfast without eggs", "category": "constraint_heavy"},

    # --- Rare / missing ingredients ---
    {"id": 11, "query": "saffron, shrimp, coconut milk", "category": "rare_ingredients"},
    {"id": 12, "query": "truffle oil and risotto rice", "category": "rare_ingredients"},
    {"id": 13, "query": "dragonfruit and coconut", "category": "rare_ingredients"},
    {"id": 14, "query": "miso paste and seaweed", "category": "rare_ingredients"},
    {"id": 15, "query": "quinoa and pomegranate", "category": "rare_ingredients"},

    # --- Ambiguous phrasing ---
    {"id": 16, "query": "something warm and comforting for a rainy day", "category": "ambiguous"},
    {"id": 17, "query": "a quick fix for a sweet tooth", "category": "ambiguous"},
    {"id": 18, "query": "impress my in-laws with dinner", "category": "ambiguous"},
    {"id": 19, "query": "something my kids won't hate", "category": "ambiguous"},

    # --- Conflicting constraints ---
    {"id": 20, "query": "vegan recipe with chicken", "category": "conflicting"},
    {"id": 21, "query": "gluten-free recipe with regular pasta", "category": "conflicting"},
    {"id": 22, "query": "dairy-free recipe with cheese", "category": "conflicting"},

    # --- Exact-match critical (allergy-style) ---
    {"id": 23, "query": "peanut-free satay sauce", "category": "exact_match_critical"},
    {"id": 24, "query": "shellfish-free seafood alternative", "category": "exact_match_critical"},
    {"id": 25, "query": "nut-free dessert without almonds", "category": "exact_match_critical"},
]

if __name__ == "__main__":
    print(f"Total eval queries: {len(eval_queries)}")
    for q in eval_queries:
        print(f"[{q['id']}] ({q['category']}) {q['query']}")