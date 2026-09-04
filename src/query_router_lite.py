import sys
import os
sys.path.append(os.path.dirname(__file__))

from constraint_parser import parse_constraints
from hybrid_search_lite import bm25_search, df
from budget import estimate_recipe_cost, is_within_budget
from guardrail import evaluate_results
from generate_response import generate_recipe_response
from nutrition import estimate_recipe_nutrition, suggest_nutrition_boost
from send_email import send_recipe_email


def extract_ingredients(query, constraints):
    constraint_words = ["without", "no", "under", "minutes", "mins", "spicy", "mild",
                         "budget", "cheap", "affordable", "vegetarian", "vegan",
                         "gluten-free", "dairy-free", "keto", "and", "with", "free"]
    tokens = [t.strip() for t in query.lower().replace(",", " ").split()]
    return [t for t in tokens if t not in constraint_words and not t.isdigit()]


def full_pipeline_lite(query, top_k=5, email_to=None, include_nutrition=False, return_meta=False):
    constraints = parse_constraints(query)
    candidate_indices, scores = bm25_search(query, top_k=top_k * 4)

    results = []
    for idx in candidate_indices:
        recipe_ingredients = df.iloc[idx]["ingredients_text"].lower()

        if "exclude" in constraints:
            if any(excluded in recipe_ingredients for excluded in constraints["exclude"]):
                continue

        if "max_budget_inr" in constraints:
            cost = estimate_recipe_cost(df.iloc[idx]["NER"])
            if not is_within_budget(cost, constraints["max_budget_inr"]):
                continue

        results.append(idx)
        if len(results) >= top_k:
            break

    query_ingredients = extract_ingredients(query, constraints)

    if not results:
        excluded_items = constraints.get("exclude", [])
        guardrail_message = (
            f"No recipes found that avoid: {', '.join(excluded_items)}."
            if excluded_items else "No matching recipes found."
        )
        should_warn = True
    else:
        should_warn, coverage_scores, guardrail_message = evaluate_results(
            query_ingredients, results, df
        )

    final_response = generate_recipe_response(query, results, df, guardrail_message)

    if include_nutrition and results:
        nutrition = estimate_recipe_nutrition(df.iloc[results[0]]["NER"])
        boost = suggest_nutrition_boost(nutrition)
        final_response += f"\n\nNutrition note: {boost}"

    if email_to:
        send_recipe_email(email_to, final_response, query)

    if return_meta:
        return {"response": final_response, "warned": should_warn}
    return final_response