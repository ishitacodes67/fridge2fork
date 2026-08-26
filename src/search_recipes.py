import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

with open("data/recipe_embeddings.pkl", "rb") as f:
    data = pickle.load(f)

embeddings = data["embeddings"]
df = data["df"]

model = SentenceTransformer("all-MiniLM-L6-v2")

def search(query, top_k=5):
    query_embedding = model.encode([query])
    similarities = cosine_similarity(query_embedding, embeddings)[0]
    top_indices = np.argsort(similarities)[::-1][:top_k]
    
    print(f"\nTop {top_k} recipes for: '{query}'\n")
    for idx in top_indices:
        print(f"- {df.iloc[idx]['title']}  (score: {similarities[idx]:.3f})")
        print(f"  Ingredients: {df.iloc[idx]['ingredients_text']}\n")

search("chicken, garlic, rice")