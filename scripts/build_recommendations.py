import ast
import json
import os
from io import BytesIO
from pathlib import Path

import boto3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

#Configuration de la session boto3 pour accéder à DynamoDB
session = boto3.Session(profile_name="Recomodo-AdminAccess-Amplify-080941085602")


#définition de variables d'environnement
#elles sont définies dans le terminal lors de l'exécution ponctuelle du script
DATA_BUCKET_NAME = os.environ["DATA_BUCKET_NAME"]
MOVIES_PARQUET_KEY = os.environ["MOVIES_PARQUET_KEY"]
GENRES_PARQUET_KEY = os.environ["GENRES_PARQUET_KEY"]

OUTPUT_PATH = os.environ.get("OUTPUT_PATH", "movie_recommendations.json")
TOP_K = int(os.environ.get("TOP_K", "5"))

s3 = session.client("s3")

def read_parquet_from_s3(bucket_name, object_key):
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    return pd.read_parquet(BytesIO(response["Body"].read()))

#transformation de la liste de liste d'id des genres en liste de strings de noms des genres
#nécéssaire que ce soit des string pour le TfidfVectorizer
def list_to_string(movies_genres, genres_dict):
    genres_string = []
    for i in movies_genres:
        temp = []
        for j in i:
            j=str(j)
            if j in genres_dict:
                temp.append(genres_dict[j])
        genres_string.append(' '.join(temp))
    return genres_string

def main() :
    #lecture des fichiers movies_clean.parquet et genres_clean.parquet
    movies = read_parquet_from_s3(DATA_BUCKET_NAME, MOVIES_PARQUET_KEY)
    genres = read_parquet_from_s3(DATA_BUCKET_NAME, GENRES_PARQUET_KEY)

    #uniformisation des types
    movies['movieId'] = movies['movieId'].astype(str)
    genres['genreId'] = genres['genreId'].astype(str)

    #création d'un dictionnaire avec les id des genres en clé et les noms des genres en valeur
    genres_dict = dict(zip(genres["genreId"], genres["name"]))

    #récupération de la colonne movieId, qui contient les id des films
    movie_ids = movies['movieId'].tolist()

    #récupération de la colonne genres, qui sont les id des genres associés à chaque film
    movies_genre = movies['genres'].fillna('[]').apply(ast.literal_eval).tolist()
    genres_string = list_to_string(movies_genre, genres_dict)

    #création d'une série avec les titres des id des films en index et les indices des films en valeur, pour pouvoir récupérer l'indice d'un film à partir de son id
    indices = pd.Series(movies.index, index=movies['movieId'])

    #création de la matrice TF-IDF à partir des genres des films
    tf = TfidfVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0.0, stop_words='english')
    tfidf_matrix = tf.fit_transform(genres_string)

    recommendations = {}

    #calcul de la similarité cosinus entre les films à partir de la matrice TF-IDF
    #retourne les 2 films les plus similaires à un film donné, en fonction de leurs genres
    for idx, movie_id in enumerate(movie_ids):
        sim_scores = linear_kernel(tfidf_matrix[idx:idx + 1], tfidf_matrix).flatten()
        ranked = sorted(enumerate(sim_scores), key=lambda x: x[1], reverse=True)

        similar_ids = []
        for other_idx,_score in ranked[1:TOP_K + 1]:
            similar_ids.append(movie_ids[other_idx])

        recommendations[movie_id] = similar_ids
    
    #écriture des recommandations dans un fichier JSON
    Path(OUTPUT_PATH).write_text(
        json.dumps(recommendations, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Wrote recommendations to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()


