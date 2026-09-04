import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi

# Load saved embeddings + dataframe
with open("data/recipe_embeddings_deploy.pkl", "rb") as f:
    data = pickle.load(f)

embeddings = data["embeddings"]
df = data["df"]

# Load the same embedding model used before
model = SentenceTransformer("all-MiniLM-L6-v2")

# --- Build BM25 index ---
# BM25 needs each document tokenized (split into words)
tokenized_corpus = [text.lower().split(", ") for text in df["ingredients_text"]]
bm25 = BM25Okapi(tokenized_corpus)

def normalize(scores):
    # Scale any list of scores to 0-1 range, so vector and BM25 scores are comparable
    scores = np.array(scores)
    if scores.max() == scores.min():
        return np.zeros_like(scores)
    return (scores - scores.min()) / (scores.max() - scores.min())

def hybrid_search(query, top_k=5, alpha=0.5):
    # alpha controls the blend: 0 = pure BM25, 1 = pure vector, 0.5 = equal mix

    # --- Vector search ---
    query_embedding = model.encode([query])
    vector_scores = cosine_similarity(query_embedding, embeddings)[0]

    # --- BM25 search ---
    tokenized_query = query.lower().split(", ")
    bm25_scores = bm25.get_scores(tokenized_query)

    # --- Combine ---
    vector_scores_norm = normalize(vector_scores)
    bm25_scores_norm = normalize(bm25_scores)
    combined_scores = alpha * vector_scores_norm + (1 - alpha) * bm25_scores_norm

    top_indices = np.argsort(combined_scores)[::-1][:top_k]

    print(f"\nTop {top_k} HYBRID results for: '{query}'\n")
    for idx in top_indices:
        print(f"- {df.iloc[idx]['title']}  "
              f"(combined: {combined_scores[idx]:.3f}, "
              f"vector: {vector_scores_norm[idx]:.3f}, "
              f"bm25: {bm25_scores_norm[idx]:.3f})")
        print(f"  Ingredients: {df.iloc[idx]['ingredients_text']}\n")

# Try the same query as yesterday for direct comparison
hybrid_search("saffron, shrimp, coconut milk")
