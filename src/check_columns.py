import pickle

with open("data/recipe_embeddings.pkl", "rb") as f:
    data = pickle.load(f)

df = data["df"]
print(df.columns.tolist())