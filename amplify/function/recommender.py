import json
import os
import boto3

from decimal import Decimal

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

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



# # Break up the big genre string into a string array
# movies['genres'] = movies['genres'].str.split('|')
# # Convert genres to string value
# movies['genres'] = movies['genres'].fillna("").astype('str')
# tf = TfidfVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0, stop_words='english')
# tfidf_matrix = tf.fit_transform(movies['genres'])
# tfidf_matrix.shape
# cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
# cosine_sim[:4, :4]
# titles = movies['title']
# indices = pd.Series(movies.index, index=movies['title'])

# # Function that get movie recommendations based on the cosine similarity score of movie genres
# def genre_recommendations(title):
#     idx = indices[title]
#     sim_scores = list(enumerate(cosine_sim[idx]))
#     sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
#     sim_scores = sim_scores[1:21]
#     movie_indices = [i[0] for i in sim_scores]
#     return titles.iloc[movie_indices]