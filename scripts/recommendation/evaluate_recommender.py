import argparse
import ast
import json
import math

import numpy as np
import pandas as pd

RATINGS_PATH = "data/dataset/rating_for_testing.csv"
MOVIES_PATH = "data/dataset/movies_cleaned.csv"
NEIGHBORS_PATH = "data/recommendation/movie_recommendations_combined.json"
TOP_K = 10
RANDOM_STATE = 42
#On considère que les films notés strictement au dessus de cette note sont "aimés" par l'utilisateur
LIKED_THRESHOLD = 7.0

#Cette metrique donne plus d'importance aux bons resultats places en haut de la liste qu'a ceux places plus bas.
def dcg_at_k(relevances, k):
    relevances = np.asarray(relevances)[:k]
    if len(relevances) == 0:
        return 0.0
    return np.sum((2 ** relevances - 1) / np.log2(np.arange(2, len(relevances) + 2)))

#Version normalisé de DCG
#Cette métrique regarde non seulement si les bons films sont recommandés, mais aussi où ils apparaissent dans la liste
def ndcg_at_k(recommended_ids, liked_ids, k):
    rel = [1 if movie_id in liked_ids else 0 for movie_id in recommended_ids[:k]]
    dcg = dcg_at_k(rel, k)
    ideal = sorted(rel, reverse=True)
    idcg = dcg_at_k(ideal, k)
    return dcg / idcg if idcg > 0 else 0.0

#Retourne la précision@k, c'est à dire , la proportion de films recommandés qui font effectivement partie des films cachés que l’utilisateur aimait vraiment
def precision_at_k(recommended_ids, liked_ids, k):
    if k == 0:
        return 0.0
    hits = sum(1 for movie_id in recommended_ids[:k] if movie_id in liked_ids)
    return hits / k

#Retourne le rappel@k, c'est à dire la proportion de films cachés que l’utilisateur aimait vraiment qui font partie des films recommandés
def recall_at_k(recommended_ids, liked_ids, k):
    if not liked_ids:
        return 0.0
    hits = sum(1 for movie_id in recommended_ids[:k] if movie_id in liked_ids)
    return hits / len(liked_ids)


# Charge le fichier JSON contenant, pour chaque film, une liste de films recommandes.
# On convertit toutes les cles et valeurs en str pour eviter les problemes de format.
def load_neighbors(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        raw_neighbors = json.load(f)

    neighbors = {}
    for movie_id, recommended_movies in raw_neighbors.items():
        movie_id = str(movie_id)
        neighbors[movie_id] = [str(candidate) for candidate in recommended_movies]

    return neighbors


def recommend_for_user(user_train, neighbors_dict, top_k=10):
    liked_train = user_train[user_train["rating"] > LIKED_THRESHOLD]["movieId"].tolist()
    seen_movies = set(user_train["movieId"].tolist())

    if not liked_train:
        return []

    scores = {}

    for liked_movie in liked_train:
        liked_movie = str(liked_movie)

        if liked_movie not in neighbors_dict:
            continue

        candidate_list = neighbors_dict[liked_movie]

        for rank, candidate_movie in enumerate(candidate_list):
            candidate_movie = str(candidate_movie)

            if candidate_movie in seen_movies:
                continue

            if candidate_movie == liked_movie:
                continue

            weight = max(len(candidate_list) - rank, 1)
            scores[candidate_movie] = scores.get(candidate_movie, 0.0) + weight

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [movie_id for movie_id, _ in ranked[:top_k]]

#Comparaison avec une recommendation par popularité
#Point de référence simple
def popularity_baseline(train_df, excluded_movie_ids, top_k=10):
    liked_train = train_df[train_df["rating"] > LIKED_THRESHOLD]
    popularity = (
        liked_train.groupby("movieId")
        .size()
        .sort_values(ascending=False)
    )

    recs = [str(movie_id) for movie_id in popularity.index if str(movie_id) not in excluded_movie_ids]
    return recs[:top_k]

#
def evaluate(ratings_df, movies_df, neighbors_dict, top_k=10):
    ratings_df["movieId"] = ratings_df["movieId"].astype(str)
    movies_df["movieId"] = movies_df["movieId"].astype(str)

    json_movie_ids = set(neighbors_dict.keys())

    common_ids = set(ratings_df["movieId"]).intersection(set(movies_df["movieId"])).intersection(json_movie_ids)

    if not common_ids:
        raise ValueError(
            "Aucun movieId en commun entre ratings, movies et le JSON. "
        )

    ratings_df = ratings_df[ratings_df["movieId"].isin(common_ids)].copy()
    movies_df = movies_df[movies_df["movieId"].isin(common_ids)].copy()

    metrics = {
        "content_precision": [],
        "content_recall": [],
        "content_ndcg": [],
        "baseline_precision": [],
        "baseline_recall": [],
        "baseline_ndcg": [],
    }

    evaluated_users = 0

    for user_id, user_ratings in ratings_df.groupby("userId"):
        liked = user_ratings[user_ratings["rating"] > LIKED_THRESHOLD].copy()

        if len(liked) < 2:
            continue

        #split aléatoire des films aimés de l'utilisateur
        liked = liked.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=False)

        test_size = max(1, math.ceil(len(liked) * 0.2))
        test_liked = liked.iloc[:test_size]
        train = user_ratings.drop(index=test_liked["index"])

        if (train["rating"] > LIKED_THRESHOLD).sum() < 1:
            continue

        ground_truth = set(test_liked["movieId"].astype(str).tolist())
        seen_movies = set(train["movieId"].astype(str).tolist())

        content_recs = recommend_for_user(
            train,
            neighbors_dict,
            top_k=top_k,
        )

        baseline_recs = popularity_baseline(
            ratings_df.drop(index=test_liked["index"]),
            excluded_movie_ids=seen_movies,
            top_k=top_k,
        )

        if not content_recs:
            continue

        metrics["content_precision"].append(precision_at_k(content_recs, ground_truth, top_k))
        metrics["content_recall"].append(recall_at_k(content_recs, ground_truth, top_k))
        metrics["content_ndcg"].append(ndcg_at_k(content_recs, ground_truth, top_k))

        metrics["baseline_precision"].append(precision_at_k(baseline_recs, ground_truth, top_k))
        metrics["baseline_recall"].append(recall_at_k(baseline_recs, ground_truth, top_k))
        metrics["baseline_ndcg"].append(ndcg_at_k(baseline_recs, ground_truth, top_k))

        evaluated_users += 1

    #calcul de la couverture du catalogue
    all_recommended = set()
    for user_id, user_ratings in ratings_df.groupby("userId"):
        recs = recommend_for_user(
            user_ratings,
            neighbors_dict,
            top_k=top_k,
        )
        all_recommended.update(recs)

    coverage = len(all_recommended) / len(common_ids) if common_ids else 0.0

    return {
        "evaluated_users": evaluated_users,
        f"content_precision@{top_k}": float(np.mean(metrics["content_precision"])) if metrics["content_precision"] else 0.0,
        f"content_recall@{top_k}": float(np.mean(metrics["content_recall"])) if metrics["content_recall"] else 0.0,
        f"content_ndcg@{top_k}": float(np.mean(metrics["content_ndcg"])) if metrics["content_ndcg"] else 0.0,
        f"baseline_precision@{top_k}": float(np.mean(metrics["baseline_precision"])) if metrics["baseline_precision"] else 0.0,
        f"baseline_recall@{top_k}": float(np.mean(metrics["baseline_recall"])) if metrics["baseline_recall"] else 0.0,
        f"baseline_ndcg@{top_k}": float(np.mean(metrics["baseline_ndcg"])) if metrics["baseline_ndcg"] else 0.0,
        "catalog_coverage": coverage,
        "common_movie_count": len(common_ids),
    }

#Permet une interpretation simple des resultats obtenus
def interpret(results, top_k):
    cp = results[f"content_precision@{top_k}"]
    bp = results[f"baseline_precision@{top_k}"]
    cn = results[f"content_ndcg@{top_k}"]
    bn = results[f"baseline_ndcg@{top_k}"]

    print("\nInterpretation")
    if cp > bp and cn > bn:
        print("Ton algo content-based bat le baseline popularite sur cet echantillon.")
    elif cp == bp and cn == bn:
        print("Ton algo et le baseline donnent des resultats tres proches.")
    else:
        print("Le baseline popularite fait aussi bien ou mieux que ton algo.")

    if cp >= 0.20:
        print("Precision plutot bonne pour un prototype simple base uniquement sur les genres.")
    elif cp >= 0.10:
        print("Precision correcte, mais encore limitee.")
    else:
        print("Precision faible : les genres seuls sont probablement trop pauvres pour bien personnaliser.")

    if results["catalog_coverage"] < 0.10:
        print("La couverture du catalogue est faible : l'algo recommande peu de films differents.")


print("Lecture des fichiers...")
ratings_df = pd.read_csv(RATINGS_PATH)
movies_df = pd.read_csv(MOVIES_PATH)
neighbors_dict = load_neighbors(NEIGHBORS_PATH)

required_ratings = {"userId", "movieId", "rating"}
required_movies = {"movieId"}

if not required_ratings.issubset(ratings_df.columns):
    raise ValueError(f"ratings doit contenir {required_ratings}")

if not required_movies.issubset(movies_df.columns):
    raise ValueError(f"movies doit contenir {required_movies}")

results = evaluate(
    ratings_df=ratings_df,
    movies_df=movies_df,
    neighbors_dict=neighbors_dict,
    top_k=TOP_K,
)

print("\n=== Resultats ===")
for key, value in results.items():
    if isinstance(value, float):
        print(f"{key}: {value:.4f}")
    else:
        print(f"{key}: {value}")

interpret(results, TOP_K)

# === Resultats (genre)===
# evaluated_users: 660
# content_precision@10: 0.0005
# content_recall@10: 0.0011
# content_ndcg@10: 0.0015
# baseline_precision@10: 0.1121
# baseline_recall@10: 0.1988
# baseline_ndcg@10: 0.3721
# catalog_coverage: 0.2346
# common_movie_count: 2306

# Interpretation
# Le baseline popularite fait aussi bien ou mieux que ton algo.
# Precision faible : les genres seuls sont probablement trop pauvres pour bien personnaliser

# === Resultats (combined)===
# evaluated_users: 660
# content_precision@10: 0.0002
# content_recall@10: 0.0000
# content_ndcg@10: 0.0005
# baseline_precision@10: 0.1121
# baseline_recall@10: 0.1988
# baseline_ndcg@10: 0.3721
# catalog_coverage: 0.4215
# common_movie_count: 2306

# Interpretation
# Le baseline popularite fait aussi bien ou mieux que ton algo.
# Precision faible : les genres seuls sont probablement trop pauvres pour bien personnaliser.