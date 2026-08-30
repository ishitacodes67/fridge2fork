from budget import estimate_recipe_cost, is_within_budget
from recognize_ingredients import recognize_ingredients_from_photo
from nutrition import estimate_recipe_nutrition, suggest_nutrition_boost
from send_email import send_recipe_email
from generate_response import generate_recipe_response
from constraint_parser import parse_constraints
from hybrid_search import hybrid_search, df, embeddings, model, bm25, normalize
from guardrail import evaluate_results
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def extract_ingredients(query, constraints):
    """
    Very rough first-pass ingredient extraction: takes the raw query,
    strips out constraint-related words, treats the rest as ingredients.
    """
    constraint_words = ["without", "no", "under", "minutes", "mins", "spicy", "mild",
                         "budget", "cheap", "affordable", "vegetarian", "vegan",
                         "gluten-free", "dairy-free", "keto", "and", "with", "free"]

    tokens = [t.strip() for t in query.lower().replace(",", " ").split()]
    ingredients = [t for t in tokens if t not in constraint_words and not t.isdigit()]
    return ingredients


def route_and_search(query, top_k=5):
    constraints = parse_constraints(query)
    constraint_keys = [k for k in constraints.keys() if k != "raw_query"]
    route = "search_with_filters" if constraint_keys else "simple_search"

    print(f"\nQuery: {query}")
    print(f"Route: {route} | Constraints: {constraint_keys}")

    query_embedding = model.encode([query])
    vector_scores = cosine_similarity(query_embedding, embeddings)[0]

    tokenized_query = query.lower().split(", ")
    bm25_scores = bm25.get_scores(tokenized_query)

    vector_scores_norm = normalize(vector_scores)
    bm25_scores_norm = normalize(bm25_scores)
    combined_scores = 0.5 * vector_scores_norm + 0.5 * bm25_scores_norm

    candidate_indices = np.argsort(combined_scores)[::-1][:top_k * 20]

    results = []
    for idx in candidate_indices:
        recipe_ingredients = df.iloc[idx]["ingredients_text"].lower()

        if "exclude" in constraints:
            if any(excluded in recipe_ingredients for excluded in constraints["exclude"]):
                continue

               # --- Apply budget filter if a specific amount was given ---
        if "max_budget_inr" in constraints:
            recipe_ingredients_list = df.iloc[idx]["NER"]
            cost = estimate_recipe_cost(recipe_ingredients_list)
            if not is_within_budget(cost, constraints["max_budget_inr"]):
                continue

        results.append(idx)
        if len(results) >= top_k:
            break
    print(f"\nTop {len(results)} results after filtering:\n")

    if not results:
        excluded_items = constraints.get("exclude", [])
        print(f"⚠️ No recipes found that avoid: {', '.join(excluded_items)} "
              f"while matching your other criteria. Try broadening your search "
              f"or checking a larger recipe database.")
    else:
        for idx in results:
            print(f"- {df.iloc[idx]['title']}")
            print(f"  Ingredients: {df.iloc[idx]['ingredients_text']}\n")

        query_ingredients = extract_ingredients(query, constraints)
        should_warn, coverage_scores, message = evaluate_results(query_ingredients, results, df)
        print(f"{message}")

    return results


def full_pipeline(query, top_k=5, email_to=None, include_nutrition=False):
    results = route_and_search(query, top_k=top_k)

    constraints = parse_constraints(query)
    query_ingredients = extract_ingredients(query, constraints)

    if not results:
        excluded_items = constraints.get("exclude", [])
        guardrail_message = (
            f"No recipes found that avoid: {', '.join(excluded_items)}."
            if excluded_items else "No matching recipes found."
        )
    else:
        should_warn, coverage_scores, guardrail_message = evaluate_results(
            query_ingredients, results, df
        )

    final_response = generate_recipe_response(query, results, df, guardrail_message)

    print("\n" + "=" * 60)
    print("FINAL GENERATED RESPONSE:")
    print("=" * 60)
    print(final_response)

    if include_nutrition and results:
        top_recipe_ingredients = df.iloc[results[0]]["NER"]
        nutrition = estimate_recipe_nutrition(top_recipe_ingredients)
        boost_suggestion = suggest_nutrition_boost(nutrition)
        print("\n" + "=" * 60)
        print("WANT TO FINISH YOUR DAILY HEALTHY DOSE?")
        print("=" * 60)
        print(f"Estimated nutrition (top recipe): {nutrition}")
        print(boost_suggestion)
        final_response += f"\n\nNutrition note: {boost_suggestion}"

    if email_to:
        send_recipe_email(email_to, final_response, query)

    return final_response


def full_pipeline_from_photo(image_path, top_k=5, email_to=None, include_nutrition=False):
    """
    Takes a photo, extracts ingredients, then runs the full pipeline exactly
    like a text or voice query would.
    """
    recognized_ingredients = recognize_ingredients_from_photo(image_path)
    print(f"Recognized ingredients from photo: {recognized_ingredients}")

    return full_pipeline(
        recognized_ingredients,
        top_k=top_k,
        email_to=email_to,
        include_nutrition=include_nutrition,
    )


if __name__ == "__main__":
    full_pipeline("chicken, rice, garlic, under ₹300", email_to="ishitakhatti5@gmail.com", include_nutrition=False)