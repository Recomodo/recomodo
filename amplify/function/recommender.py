import json
import os
import boto3

from decimal import Decimal

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd
import pyarrow as pa
import ast

# #Configuration de la session boto3 pour accéder à DynamoDB 
# # ATTENTION : NE PAS UTILISER CETTE CONFIGURATION EN PRODUCTION, ELLE EST UNIQUEMENT DESTINÉE À DES FINS DE TESTS LOCAUX
# session = boto3.Session(profile_name="Recomodo-AdminAccess-Amplify-080941085602")

# dynamodb = session.resource("dynamodb") #remplacer session par boto3 lors de la production

# #Accès aux tables DynamoDB
# movies_table = dynamodb.Table("Movie-pmu5tm5u2vfw5gpeaqtiqqs2be-NONE")
# #genres_table = dynamodb.Table("Genre-pmu5tm5u2vfw5gpeaqtiqqs2be-NONE")

# genres_table = []

# #Pour transformer les Decimal en float pour le json.dumps
# class DecimalEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, Decimal):
#             return float(obj)
#         return super().default(obj)


#lecture des fichiers movies_clean.parquet et genres_clean.parquet
movies = pd.read_parquet("movies_clean.parquet")
genres = pd.read_parquet("genres_clean.parquet")

#création d'un dictionnaire avec les id des genres en clé et les noms des genres en valeur
genres_dict = dict(zip(genres["genreId"], genres["name"]))

#récupération de la colonne title, qui contient les titres des films
titles = movies['title'].tolist()
#création d'une série avec les titres des films en index et les indices des films en valeur, pour pouvoir récupérer l'indice d'un film à partir de son titre
indices = pd.Series(movies.index, index=movies['title'])

#récupération de la colonne genres, qui sont les id des genres associés à chaque film
movies_genre = movies['genres'].fillna('[]').apply(ast.literal_eval).tolist()

#transformation de la liste de liste d'id des genres en liste de strings de noms des genres
#nécéssaire que ce soit des string pour le TfidfVectorizer
genres_n = []
for i in genres:
    temp = []
    for j in i:
        if j in genres_dict:
            temp.append(genres_dict[j])
    genres_n.append(' '.join(temp))


#création de la matrice TF-IDF à partir des genres des films
tf = TfidfVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0, stop_words='english')
tfidf_matrix = tf.fit_transform(genres_n)

#calcul de la similarité cosinus entre les films à partir de la matrice TF-IDF
def genre_recommendations(title):
    idx = indices[title]

    sim_scores = linear_kernel(tfidf_matrix[idx:idx+1], tfidf_matrix).flatten()
    sim_scores = list(enumerate(sim_scores))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    sim_scores = sim_scores[1:21]
    movie_indices = [i[0] for i in sim_scores]
    return [titles[i] for i in movie_indices]



def handler(event, context):
    # #Récupération de tous les films depuis la table DynamoDB
    # response = movies_table.scan()
    # movies = response.get("Items", [])

    # #Récupération d'un film spécifique pour tester l'accès à la table DynamoDB
    # single_movie_response = movies_table.get_item(Key={"id": "3635"})
    # movie = single_movie_response.get("Item")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "count": len(movie),
            "movies": movie
        }, cls=DecimalEncoder)
    }

if __name__ == "__main__":
    print(handler({}, None))

