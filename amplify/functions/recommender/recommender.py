import json
import os
import boto3
from boto3.dynamodb.conditions import Key

#Configuration de la session boto3 pour accéder à DynamoDB 
# ATTENTION : NE PAS UTILISER CETTE CONFIGURATION EN PRODUCTION, ELLE EST UNIQUEMENT DESTINÉE À DES FINS DE TESTS LOCAUX
#session = boto3.Session(profile_name="Recomodo-AdminAccess-Amplify-080941085602")

dynamodb = boto3.resource("dynamodb") #remplacer session par boto3 pour le prod
s3 = boto3.client("s3") #remplacer session par boto3 pour le prod

#variable d'environnement pour le nom de la table DynamoDB
RATINGS_TABLE_NAME = os.environ.get("RATINGS_TABLE_NAME")
RATINGS_USER_ID_INDEX = os.environ.get("RATINGS_USER_ID_INDEX")
#variable d'environnement pour le nom du bucket S3 et la clé du fichier json qui contient les recommandations pré-calculées pour chaque film, généré par le script build_recommendations.py
DATA_BUCKET_NAME = os.environ.get("DATA_BUCKET_NAME")
MOVIES_RECOMMENDATIONS_KEY = os.environ.get("MOVIES_RECOMMENDATIONS_KEY")

ratings_table = dynamodb.Table(RATINGS_TABLE_NAME)
_recommendations_cache = None #cache pour stocker les recommandations pré-calculées, pour éviter de faire une requête S3 à chaque appel de la fonction handler

LIKED_THRESHOLD = 7
DISLIKED_THRESHOLD = 3.5

#permet de récuperer les recommandations depuis le bucket S3, elles sont stockées dans un fichier JSON
def load_recommendations_from_s3():
    global _recommendations_cache
    if _recommendations_cache is None:
        response = s3.get_object(Bucket=DATA_BUCKET_NAME, Key=MOVIES_RECOMMENDATIONS_KEY)
        _recommendations_cache = json.loads(response["Body"].read().decode("utf-8"))
    return _recommendations_cache

#on récupère l'id du user qui demande la recommandation
#on teste plusieurs endroits où l'id peut être présent dans l'event, pour être sûr de le récupérer
def extract_user_id(event):
    if "userId" in event: #si userId est directement à la racine de l'event
        return event["userId"]
    elif event.get("arguments") and "userId" in event["arguments"]: #si l'event contient une clé arguments et que userId est dedans
        return event["arguments"]["userId"]
    return None

#on récupère les ratings de l'utilisateur dans la table DynamoDB à partir de son userId
#retourne une liste de dictionnaires, chaque dictionnaire représentant un rating avec les clés "movieId", "userId" et "rating" 
def get_user_ratings(user_id):
    response = ratings_table.query(
        IndexName=RATINGS_USER_ID_INDEX,
        KeyConditionExpression=Key("userId").eq(user_id)
    )
    return response.get("Items", [])


#on récupère la liste finale des recommendations pour l'utilisateur
def get_recommendations_for_user(user_ratings, already_rated_movies, recommendations_map, limit=15):
    scores = {}
    seen = {str(movie_id) for movie_id in already_rated_movies}

    #Pour chaque film noté on calcul un score
    for item in user_ratings:
        movie_id = item.get("movieId")
        rating = float(item.get("rating",0))

        if movie_id is None:
            continue

        movie_id = str(movie_id)
        #On récupère les films similaires au film noté
        recs = recommendations_map.get(movie_id, [])

        #Pondération positive sur les films similaires, si l'utilisateur à aimé le film
        if rating >= LIKED_THRESHOLD:
            user_weight = rating
            for rank, rec in enumerate(recs, start=1):
                rec = str(rec)

                if rec in seen or rec == movie_id:
                    continue

                rank_weight = 1/rank
                scores[rec] = scores.get(rec,0.0) + (user_weight*rank_weight)
        
        #Pondération négative sur les films similaires, si l'utilisateur n'a pas aimé le film
        elif rating <= DISLIKED_THRESHOLD:
            user_weight = 10-rating
            for rank, rec in enumerate(recs, start=1):
                rec = str(rec)

                if rec in seen or rec == movie_id:
                    continue

                rank_weight = 1/rank
                scores[rec] = scores.get(rec,0.0) - (user_weight*rank_weight)
    
    #On récupère uniquement les films avec un score positif et on les tri dans l'ordre décroissant
    ranked = sorted(
        ((movie_id,score) for movie_id, score in scores.items() if score > 0),
        key=lambda x: x[1],
        reverse=True

    )
    return [movie_id for movie_id, _ in ranked[:limit]]

def handler(event, context):
    user_id = extract_user_id(event)

    if not user_id: #erreur si on ne trouve pas l'id de l'utilisateur dans l'event
        raise ValueError("userId not found in event")
    
    user_ratings = get_user_ratings(user_id)

    if not user_ratings: #erreur si l'utilisateur n'a pas de ratings dans la table DynamoDB
        return {
            "userId": user_id,
            "recommendations": []
        }
    
    recommendations_map = load_recommendations_from_s3()
    #top_movies = top_rated_movies(user_ratings)
    #bottom_movies = bottom_rated_movies(user_ratings)
    already_rated_movies_ids = {
        str(item.get("movieId")) 
        for item in user_ratings 
        if item.get("movieId") is not None}
    
    recommendations = get_recommendations_for_user(user_ratings, already_rated_movies_ids, recommendations_map)
    return {
        "userId": user_id,
        "recommendations": recommendations
    }

# if __name__ == "__main__":
#     test_event = {
#     "arguments": {"userId": "tmdb_150"}
#     }
#     print(handler(test_event, None))