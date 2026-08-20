import pandas as pd
import ast

# Only load first 5000 rows for now — much faster while testing
df = pd.read_csv("data/RecipeNLG_dataset.csv", nrows=5000)

df = df.drop(columns=["Unnamed: 0"])
df = df.dropna(subset=["title"])

df["NER"] = df["NER"].apply(ast.literal_eval)

print(type(df["NER"].iloc[0]))
print(df["NER"].iloc[0])

df_sample = df.sample(2000, random_state=42)
df_sample.to_csv("data/recipes_sample.csv", index=False)
print("\nSaved sample of", len(df_sample), "recipes to data/recipes_sample.csv")