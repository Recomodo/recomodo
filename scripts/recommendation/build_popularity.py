import json

import pandas as pd

RATINGS_PATH = "data/dataset/rating_for_testing.csv"
OUTPUT_PATH = "data/recommendation/movie_popularity.json"
LIKED_THRESHOLD = 7.0


print("Lecture du fichier ratings...")
ratings_df = pd.read_csv(RATINGS_PATH)

required_columns = {"movieId", "rating"}
if not required_columns.issubset(ratings_df.columns):
    raise ValueError(f"Le fichier ratings doit contenir les colonnes {required_columns}")

ratings_df["movieId"] = ratings_df["movieId"].astype(str)

# On garde uniquement les films "aimes"
liked_df = ratings_df[ratings_df["rating"] > LIKED_THRESHOLD].copy()

if liked_df.empty:
    raise ValueError("Aucun film aime trouve dans le fichier ratings.")

# Popularite brute = nombre de fois ou le film a ete aime
movie_popularity = liked_df.groupby("movieId").size()

min_val = movie_popularity.min()
max_val = movie_popularity.max()

# Normalisation entre 0 et 1
if min_val == max_val:
    popularity_scores = {
        str(movie_id): 1.0
        for movie_id in movie_popularity.index
    }
else:
    popularity_scores = {
        str(movie_id): float((count - min_val) / (max_val - min_val))
        for movie_id, count in movie_popularity.items()
    }

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(popularity_scores, f, ensure_ascii=False, indent=2)

print(f"Fichier ecrit : {OUTPUT_PATH}")
print(f"Nombre de films avec score de popularite : {len(popularity_scores)}")
print(f"Popularite min brute : {min_val}")
print(f"Popularite max brute : {max_val}")
