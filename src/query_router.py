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

    # --- Run hybrid search scoring ---
    query_embedding = model.encode([query])
    vector_scores = cosine_similarity(query_embedding, embeddings)[0]

    tokenized_query = query.lower().split(", ")
    bm25_scores = bm25.get_scores(tokenized_query)

    vector_scores_norm = normalize(vector_scores)
    bm25_scores_norm = normalize(bm25_scores)
    combined_scores = 0.5 * vector_scores_norm + 0.5 * bm25_scores_norm

    # Get a large candidate pool so filtering still leaves enough results
    candidate_indices = np.argsort(combined_scores)[::-1][:top_k * 20]

    results = []
    for idx in candidate_indices:
        recipe_ingredients = df.iloc[idx]["ingredients_text"].lower()

        # --- Apply hard exclusion filter ---
        if "exclude" in constraints:
            if any(excluded in recipe_ingredients for excluded in constraints["exclude"]):
                continue  # skip this recipe, it violates an exclusion

        results.append(idx)
        if len(results) >= top_k:
            break

    # Print results ONCE, after filtering is fully done
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

        # --- Run the guardrail check on final results (only if we have results) ---
        query_ingredients = extract_ingredients(query, constraints)
        should_warn, coverage_scores, message = evaluate_results(query_ingredients, results, df)
        print(f"{message}")

    return results

def full_pipeline(query, top_k=5, email_to=None):
    """
    The complete end-to-end flow: parse -> retrieve -> filter -> guardrail -> generate.
    If email_to is provided, also emails the result.
    """
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

    if email_to:
        send_recipe_email(email_to, final_response, query)

    return final_response

if __name__ == "__main__":
    full_pipeline("chicken, garlic, rice", email_to="ishitakhatti5@gmail.com")