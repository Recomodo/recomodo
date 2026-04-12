import json
import os
import boto3
import pandas as pd
import ast

from decimal import Decimal
from boto3.dynamodb.conditions import Key
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel



#Configuration de la session boto3 pour accéder à DynamoDB 
# ATTENTION : NE PAS UTILISER CETTE CONFIGURATION EN PRODUCTION, ELLE EST UNIQUEMENT DESTINÉE À DES FINS DE TESTS LOCAUX
session = boto3.Session(profile_name="Recomodo-AdminAccess-Amplify-080941085602")

dynamodb = session.resource("dynamodb") #remplacer session par boto3 lors de la production

#variable d'environnement pour le nom de la table DynamoDB
RATINGS_TABLE_NAME = os.environ["RATINGS_TABLE_NAME"]

ratings_table = dynamodb.Table(RATINGS_TABLE_NAME)


#Pour transformer les Decimal en float pour le json.dumps
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


#lecture des fichiers movies_clean.parquet et genres_clean.parquet
movies = pd.read_parquet("movies_clean.parquet")
genres = pd.read_parquet("genres_clean.parquet")

#création d'un dictionnaire avec les id des genres en clé et les noms des genres en valeur
genres_dict = dict(zip(genres["genreId"], genres["name"]))

#récupération de la colonne title, qui contient les titres des films
movie_id = movies['movieId'].tolist()
#création d'une série avec les titres des id des films en index et les indices des films en valeur, pour pouvoir récupérer l'indice d'un film à partir de son id
indices = pd.Series(movies.index, index=movies['movieId'])

#récupération de la colonne genres, qui sont les id des genres associés à chaque film
movies_genre = movies['genres'].fillna('[]').apply(ast.literal_eval).tolist()


#transformation de la liste de liste d'id des genres en liste de strings de noms des genres
#nécéssaire que ce soit des string pour le TfidfVectorizer
def list_to_string(genres):
    genres_string = []
    for i in genres:
        temp = []
        for j in i:
            if j in genres_dict:
                temp.append(genres_dict[j])
        genres_string.append(' '.join(temp))
    return genres_string

genres_string = list_to_string(movies_genre)

#création de la matrice TF-IDF à partir des genres des films
tf = TfidfVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0, stop_words='english')
tfidf_matrix = tf.fit_transform(genres_string)


#calcul de la similarité cosinus entre les films à partir de la matrice TF-IDF
#retourne les 2 films les plus similaires à un film donné, en fonction de leurs genres
def genre_recommendations(id):
    idx = indices[id]

    sim_scores = linear_kernel(tfidf_matrix[idx:idx+1], tfidf_matrix).flatten()
    sim_scores = list(enumerate(sim_scores))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    sim_scores = sim_scores[1:5] #ne commence pas à 0 pour ne pas recommander le film lui-même
    movie_indices = [i[0] for i in sim_scores]
    return [movie_id[i] for i in movie_indices]



#on récupère l'id du user qui demande la recommandation
#on teste plusieurs endroits où l'id peut être présent dans l'event, pour être sûr de le récupérer
def extract_user_id(event):
    if "userId" in event: #si userId est directement à la racine de l'event
        return event["userId"]
    elif event.get("arguments") and "userId" in event["arguments"]: #si l'event contient une clé arguments et que userId est dedans
        return event["arguments"]["userId"]
    elif event.get("queryStringParameters") and "userId" in event["queryStringParameters"]: #si userId est dans les paramètre d'URL
        return event["queryStringParameters"]["userId"]
    elif event.get("pathParameters") and "userId" in event["pathParameters"]: #si userId est dans les paramètres de chemin
        return event["pathParameters"]["userId"]
    elif event.get("body"): #si la requête contient un corps
        body =  event["body"]
        if isinstance(body, str):
            body = json.loads(body)
        if "userId" in body: #si userId est dans le corps de la requête
            return body["userId"]
    return None

#on récupère les ratings de l'utilisateur dans la table DynamoDB à partir de son userId
#retourne une liste de dictionnaires, chaque dictionnaire représentant un rating avec les clés "movieId", "userId" et "rating" 
def get_user_ratings(user_id):
    response = ratings_table.query( 
        KeyConditionExpression=Key("userId").eq(user_id) #on cherche les ratings de l'utilisateur dans la table DynamoDB en utilisant son userId comme clé de partition
    )
    return response.get("Items", [])

#on récupére les films les mieux notés de l'utilisateur
def top_rated_movies(user_ratings,limit=5):
    sorted_ratings = sorted(user_ratings, key = lambda x : float(x.get("rating",0)), reverse = True)

    top_movies = []
    for i in sorted_ratings :
        movie_id = i.get("movieId")
        if movie_id is not None:
            top_movies.append(movie_id)
    return top_movies[:limit]

#on récupère la liste finale des recommendations pour l'utilisateur
def get_recommendations_for_user(top_movies_id, already_rated_movies):
    recommendations = []
    seen = set(already_rated_movies) 
    for movie_id in top_movies_id:
        recs = genre_recommendations(movie_id)

        for rec in recs:
            if rec not in seen and rec not in recommendations: #pour éviter les films déjà notés ou déja dans la liste
                recommendations.append(rec)
                seen.add(rec)
    return recommendations


def handler(event, context):
    user_id = extract_user_id(event)

    if not user_id: #erreur si on ne trouve pas l'id de l'utilisateur dans l'event
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "missing userId"})
        }
    
    user_ratings = get_user_ratings(user_id)

    if not user_ratings: #erreur si l'utilisateur n'a pas de ratings dans la table DynamoDB
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "no ratings found for user"})
        }

    top_movies = top_rated_movies(user_ratings)
    already_rated_movies_ids = {item.get("movieId") for item in user_ratings if item.get("movieId") is not None}
    recommendations = get_recommendations_for_user(top_movies, already_rated_movies_ids)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "userId": user_id,
            "recommendations": recommendations,
        }, cls=DecimalEncoder)
    }

if __name__ == "__main__":
    print(handler({}, None))

