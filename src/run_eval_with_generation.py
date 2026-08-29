import sys
import os
import time
import csv

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data"))

from query_router import full_pipeline
from eval_queries import eval_queries

# Pick a representative sample across categories instead of all 25,
# to conserve free-tier rate limits during testing
sample_ids = [1, 6, 9, 11, 20, 24, 25]  # easy, constraint, vegan-fail, rare, conflicting, 2x safety-critical
sample_queries = [q for q in eval_queries if q["id"] in sample_ids]

rows = []

for item in sample_queries:
    print(f"\n\n{'#'*70}")
    print(f"# [{item['id']}] ({item['category']}) {item['query']}")
    print('#'*70)

    try:
        final_response = full_pipeline(item["query"], top_k=5)
        rows.append({
            "id": item["id"],
            "category": item["category"],
            "query": item["query"],
            "generated_response": final_response,
            "manual_label": "",
        })
    except Exception as e:
        print(f"ERROR: {e}")
        rows.append({
            "id": item["id"],
            "category": item["category"],
            "query": item["query"],
            "generated_response": f"ERROR: {e}",
            "manual_label": "",
        })

    time.sleep(3)  # stay well under 30 requests/minute rate limit

# Save results
output_path = "data/eval_generation_results.csv"
with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"\n\nSaved {len(rows)} generation results to {output_path}")