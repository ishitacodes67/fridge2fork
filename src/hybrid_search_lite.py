import pandas as pd
import pickle
import ast
from rank_bm25 import BM25Okapi
import numpy as np

with open("data/recipe_embeddings_deploy.pkl", "rb") as f:
    data = pickle.load(f)

df = data["df"]

tokenized_corpus = [text.lower().split(", ") for text in df["ingredients_text"]]
bm25 = BM25Okapi(tokenized_corpus)


def normalize(scores):
    scores = np.array(scores)
    if scores.max() == scores.min():
        return np.zeros_like(scores)
    return (scores - scores.min()) / (scores.max() - scores.min())


def bm25_search(query, top_k=20):
    """Pure BM25 keyword search — no embeddings, no PyTorch, minimal memory."""
    tokenized_query = query.lower().replace(",", " ").split()
    scores = bm25.get_scores(tokenized_query)
    scores_norm = normalize(scores)
    top_indices = np.argsort(scores_norm)[::-1][:top_k]
    return top_indices, scores_norm
