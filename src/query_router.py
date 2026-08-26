from constraint_parser import parse_constraints
from hybrid_search import hybrid_search, df, embeddings, model, bm25, normalize
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def route_and_search(query, top_k=5):
    constraints = parse_constraints(query)
    constraint_keys = [k for k in constraints.keys() if k != "raw_query"]
    route = "search_with_filters" if constraint_keys else "simple_search"

    print(f"\nQuery: {query}")
    print(f"Route: {route} | Constraints: {constraint_keys}")

    # --- Run hybrid search as before, but get more candidates than needed ---
    # (since some will get filtered out)
    query_embedding = model.encode([query])
    vector_scores = cosine_similarity(query_embedding, embeddings)[0]

    tokenized_query = query.lower().split(", ")
    bm25_scores = bm25.get_scores(tokenized_query)

    vector_scores_norm = normalize(vector_scores)
    bm25_scores_norm = normalize(bm25_scores)
    combined_scores = 0.5 * vector_scores_norm + 0.5 * bm25_scores_norm

    # Get more candidates than top_k, so filtering still leaves enough results
    candidate_indices = np.argsort(combined_scores)[::-1][:top_k * 4]

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

    print(f"\nTop {len(results)} results after filtering:\n")
    for idx in results:
        print(f"- {df.iloc[idx]['title']}")
        print(f"  Ingredients: {df.iloc[idx]['ingredients_text']}\n")

    return results


if __name__ == "__main__":
    route_and_search("chicken casserole without mushrooms")