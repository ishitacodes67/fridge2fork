import pandas as pd
import pickle
from sentence_transformers import SentenceTransformer
import ast

df = pd.read_csv("data/recipes_sample.csv")
df["NER"] = df["NER"].apply(ast.literal_eval)
df["ingredients_text"] = df["NER"].apply(lambda x: ", ".join(x))

df_small = df.sample(500, random_state=42).reset_index(drop=True)

model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(df_small["ingredients_text"].tolist(), show_progress_bar=True)

with open("data/recipe_embeddings_deploy.pkl", "wb") as f:
    pickle.dump({"embeddings": embeddings, "df": df_small}, f)

print("Saved smaller deployment embeddings:", len(df_small), "recipes")