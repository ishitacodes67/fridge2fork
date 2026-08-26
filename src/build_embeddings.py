import pandas as pd
from sentence_transformers import SentenceTransformer
import pickle
import ast

# Load your small sample (fast to work with)
df = pd.read_csv("data/recipes_sample.csv")

# Convert the NER column back into a real list (it's saved as a string in the CSV)
df["NER"] = df["NER"].apply(ast.literal_eval)

# Turn each recipe's ingredient list into a single text string for embedding
df["ingredients_text"] = df["NER"].apply(lambda ingredients: ", ".join(ingredients))

# Load the pretrained embedding model (downloads once, then cached locally)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Convert every recipe's ingredient text into an embedding vector
print("Generating embeddings for", len(df), "recipes...")
embeddings = model.encode(df["ingredients_text"].tolist(), show_progress_bar=True)

# Save both the embeddings and the dataframe together
with open("data/recipe_embeddings.pkl", "wb") as f:
    pickle.dump({"embeddings": embeddings, "df": df}, f)

print("Done. Saved embeddings to data/recipe_embeddings.pkl")