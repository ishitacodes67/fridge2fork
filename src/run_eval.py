import sys
import os
import csv

# Make sure we can import from src/ and data/
sys.path.append(os.path.join(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data"))

from query_router import route_and_search, extract_ingredients
from constraint_parser import parse_constraints
from guardrail import evaluate_results
import pickle

# Load eval queries
sys.path.append("data")
from eval_queries import eval_queries

# Load dataframe (needed for guardrail check inside route_and_search already,
# but we reload here too for standalone safety)
with open("data/recipe_embeddings.pkl", "rb") as f:
    data = pickle.load(f)
df = data["df"]

def run_all_evals():
    rows = []

    for item in eval_queries:
        qid = item["id"]
        query = item["query"]
        category = item["category"]

        print(f"\n{'='*60}")
        print(f"[{qid}] ({category}) Running: {query}")
        print('='*60)

        try:
            results = route_and_search(query, top_k=5)

            constraints = parse_constraints(query)
            query_ingredients = extract_ingredients(query, constraints)
            should_warn, coverage_scores, message = evaluate_results(query_ingredients, results, df)

            top_titles = [df.iloc[idx]["title"] for idx in results] if results else []

            rows.append({
                "id": qid,
                "category": category,
                "query": query,
                "num_results": len(results) if results else 0,
                "top_titles": " | ".join(top_titles),
                "avg_coverage": round(sum(coverage_scores) / len(coverage_scores), 2) if coverage_scores else 0,
                "guardrail_warned": should_warn,
                "guardrail_message": message,
                "manual_label": "",  # you'll fill this in by hand after reviewing
                "notes": "",         # you'll fill this in too
            })

        except Exception as e:
            print(f"ERROR on query {qid}: {e}")
            rows.append({
                "id": qid,
                "category": category,
                "query": query,
                "num_results": 0,
                "top_titles": "",
                "avg_coverage": 0,
                "guardrail_warned": "ERROR",
                "guardrail_message": str(e),
                "manual_label": "",
                "notes": "",
            })

    # Save everything to a CSV for review
    output_path = "data/eval_results.csv"
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n\nSaved {len(rows)} eval results to {output_path}")


if __name__ == "__main__":
    run_all_evals()
    