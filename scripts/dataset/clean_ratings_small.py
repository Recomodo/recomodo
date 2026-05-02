import pandas as pd

RATINGS_PATH = "data/dataset/ratings_small.csv"
MOVIES_PATH = "data/dataset/movies_cleaned.csv"
OUTPUT_PATH = "data/dataset/ratings_small_cleaned.csv"


print("Lecture du fichier ratings...")
ratings_df = pd.read_csv(RATINGS_PATH)
print(f"{len(ratings_df)} ratings lus")

print("Lecture de la liste des films valides...")
movies_df = pd.read_csv(MOVIES_PATH, usecols=["movieId"])
valid_movie_ids = set(movies_df["movieId"].astype(str))

ratings_df["movieId"] = ratings_df["movieId"].astype(str)
ratings_df = ratings_df[ratings_df["movieId"].isin(valid_movie_ids)].copy()
print(f"{len(ratings_df)} ratings apres filtrage sur les films existants")

ratings_df["userId"] = ratings_df["userId"].apply(lambda value: f"tmdb_{int(value)}")
ratings_df["rating"] = ratings_df["rating"].apply(lambda value: round(float(value) * 2, 1))

ratings_df.to_csv(OUTPUT_PATH, index=False, columns=["userId", "movieId", "rating"])

print(f"Fichier nettoye ecrit dans : {OUTPUT_PATH}")
print(f"Ratings exportes : {len(ratings_df)}")
