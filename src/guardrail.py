def check_coverage(query_ingredients, recipe_ingredients_text):
    """
    Checks what fraction of query ingredients actually appear in a recipe.
    query_ingredients: list of ingredient strings the user mentioned
    recipe_ingredients_text: the recipe's ingredient string (lowercase)
    """
    if not query_ingredients:
        return 1.0  # nothing to check against, treat as fully covered

    matched = sum(1 for ing in query_ingredients if ing.lower() in recipe_ingredients_text.lower())
    return matched / len(query_ingredients)


def evaluate_results(query_ingredients, results, df, coverage_threshold=0.5):
    """
    Given a list of result indices, checks average coverage.
    Returns (should_warn: bool, coverage_scores: list, message: str)
    """
    coverage_scores = []
    for idx in results:
        recipe_text = df.iloc[idx]["ingredients_text"]
        coverage = check_coverage(query_ingredients, recipe_text)
        coverage_scores.append(coverage)

    avg_coverage = sum(coverage_scores) / len(coverage_scores) if coverage_scores else 0

    should_warn = avg_coverage < coverage_threshold

    if should_warn:
        missing_pct = int((1 - avg_coverage) * 100)
        message = (f"⚠️ Heads up: these results only partially match what you asked for "
                   f"(~{missing_pct}% of your ingredients weren't found in these recipes). "
                   f"You may want to try different ingredients or check the recipes carefully.")
    else:
        message = "✅ These results are a strong match for your ingredients."

    return should_warn, coverage_scores, message


# Quick manual test
if __name__ == "__main__":
    import pickle
    with open("data/recipe_embeddings.pkl", "rb") as f:
        data = pickle.load(f)
    df = data["df"]

    # Simulate: user asked for saffron, shrimp, coconut milk
    # but our dataset mostly doesn't have saffron/coconut milk
    query_ingredients = ["saffron", "shrimp", "coconut milk"]
    
    # Pretend these are the top result indices from Day 4's search
    fake_results = df[df["ingredients_text"].str.contains("shrimp", case=False)].index[:5].tolist()

    should_warn, scores, message = evaluate_results(query_ingredients, fake_results, df)
    print("Coverage scores per result:", scores)
    print("\n", message)