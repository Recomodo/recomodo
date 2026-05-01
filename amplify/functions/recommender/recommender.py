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
POPULARITY_KEY = os.environ.get("POPULARITY_KEY")

ratings_table = dynamodb.Table(RATINGS_TABLE_NAME)
_recommendations_cache = None #cache pour stocker les recommandations pré-calculées, pour éviter de faire une requête S3 à chaque appel de la fonction handler
_popularity_cache = None

LIKED_THRESHOLD = 7
DISLIKED_THRESHOLD = 3.5
ALPHA = 0.15
BETA = 0.85
GAMMA = 0.10


#permet de récuperer les recommandations depuis le bucket S3, elles sont stockées dans un fichier JSON
def load_recommendations_from_s3():
    global _recommendations_cache
    if _recommendations_cache is None:
        response = s3.get_object(Bucket=DATA_BUCKET_NAME, Key=MOVIES_RECOMMENDATIONS_KEY)
        _recommendations_cache = json.loads(response["Body"].read().decode("utf-8"))
    return _recommendations_cache 

#permet de récupérer les scores de popularité déjà calculer
def load_popularity_from_s3():
    global _popularity_cache
    if _popularity_cache is None:
        response = s3.get_object(Bucket=DATA_BUCKET_NAME, Key=POPULARITY_KEY)
        _popularity_cache = json.load(response["Body"].read().decode("utf-8"))
    return _popularity_cache

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
def get_recommendations_for_user(user_ratings, already_rated_movies, recommendations_map, popularity_map, limit=15):
    content_scores = {}
    final_scores = {}
    seen = {str(movie_id) for movie_id in already_rated_movies}

    # Pour chaque film noté, on calcule un score de contenu
    for item in user_ratings:
        movie_id = item.get("movieId")
        rating = float(item.get("rating", 0))

        if movie_id is None:
            continue

        movie_id = str(movie_id)

        # On récupère les films similaires au film noté
        recs = recommendations_map.get(movie_id, [])

        # Pondération positive sur les films similaires, si l'utilisateur a aimé le film
        if rating >= LIKED_THRESHOLD:
            user_weight = rating

            for rank, rec in enumerate(recs, start=1):
                rec = str(rec)

                if rec in seen or rec == movie_id:
                    continue

                rank_weight = 1 / rank
                content_scores[rec] = content_scores.get(rec, 0.0) + (user_weight * rank_weight)

        # Pondération négative sur les films similaires, si l'utilisateur n'a pas aimé le film
        elif rating <= DISLIKED_THRESHOLD:
            user_weight = 10 - rating

            for rank, rec in enumerate(recs, start=1):
                rec = str(rec)

                if rec in seen or rec == movie_id:
                    continue

                rank_weight = 1 / rank
                content_scores[rec] = content_scores.get(rec, 0.0) - (user_weight * rank_weight)

    positive_content_scores = {
        movie_id : score
        for movie_id, score in content_scores.items()
        if score > 0
    }

    if not positive_content_scores:
        return []
    
    #Normalisation des score de contenu
    min_content = min(positive_content_scores.values())
    max_content = max(positive_content_scores.values())

    if min_content == max_content:
        normalized_content_score = {
            movie_id : 1.0
            for movie_id in positive_content_scores.keys()
        }
    else:
        normalized_content_score = {
            movie_id : (score - min_content)/(max_content - min_content)
            for movie_id, score in positive_content_scores.items()
        }

    # On combine ensuite le score de contenu et le score de popularité
    for movie_id, content_score in normalized_content_score.items():
        popularity_score = float(popularity_map.get(str(movie_id), 0.0))
        # Le score final garde principalement le contenu
        # et ajoute un petit bonus de popularité
        final_scores[movie_id] = (ALPHA * content_score) + (BETA * popularity_score)

    # On trie les films dans l'ordre décroissant de score final
    #on prend les 50 meilleurs et on va les retrier avec un critère de diversité
    ranked_candidates = sorted(
        final_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )
    candidate_ids = [movie_id for movie_id, _ in ranked_candidates[:50]]

    selected = []
    while candidate_ids and len(selected)<limit:
        best_movie = None
        best_score = float("-inf")
        for candidate in candidate_ids:
            score = final_scores[candidate]

            #pénalité si le film est trop proche des films déjà sélectionnés
            diversity_penality = 0.0
            for chosen in selected:
                chosen_neighbors = recommendations_map.get(str(chosen),[])
                if candidate in chosen_neighbors:
                    diversity_penality += 1.0
            
            reranked_score = score - GAMMA * diversity_penality

            if reranked_score > best_score:
                best_movie = candidate
                best_score = reranked_score
        
        selected.append(best_movie)
        candidate_ids.remove(best_movie)
    return selected

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
    popularity_map = load_popularity_from_s3()

    already_rated_movies_ids = {
        str(item.get("movieId")) 
        for item in user_ratings 
        if item.get("movieId") is not None}
    
    recommendations = get_recommendations_for_user(user_ratings, already_rated_movies_ids, recommendations_map, popularity_map)
    return {
        "userId": user_id,
        "recommendations": recommendations
    }

# if __name__ == "__main__":
#     test_event = {
#     "arguments": {"userId": "a119909e-f031-701f-7b70-f0471de2d079"}
#     }
#     print(handler(test_event, None))