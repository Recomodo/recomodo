import json
import os
import boto3

s3 = boto3.client("s3")

DATA_BUCKET_NAME = os.environ.get("DATA_BUCKET_NAME")
MOVIES_RECOMMENDATIONS_KEY = os.environ.get("MOVIES_RECOMMENDATIONS_KEY")

_similar_cache = None
 
# Charge le fichier JSON depuis S3 qui contient pour chaque film
# la liste de ses films similaires, précalculée par build_recommendations.py.
def load_recommendations_from_s3():
    global _similar_cache
    if _similar_cache is None:
        response = s3.get_object(Bucket=DATA_BUCKET_NAME, Key=MOVIES_RECOMMENDATIONS_KEY)
        _similar_cache = json.loads(response["Body"].read().decode("utf-8"))
    return _similar_cache
 
 
# Cherche "movieId" à plusieurs endroits dans l'event car selon comment
# le front appelle le Lambda, il peut être à des endroits différents
def extract_movie_id(event):
    if "movieId" in event:
        return event["movieId"]
    elif event.get("arguments") and "movieId" in event["arguments"]:
        return event["arguments"]["movieId"]
    return None
 
 
def handler(event, context):
    # Le front envoie : {"movieId": "123"}
    movie_id = extract_movie_id(event)
 
    if not movie_id: #si on n'a pas réussi à extraire le movieId de l'event, on retourne une erreur
        raise ValueError("movieId not found in event")
 
    recommendations_map = load_recommendations_from_s3()
 
    # On récupère directement la liste des films similaires pour ce movieId.
    # Si le film n'est pas dans le JSON (movieId inconnu), on retourne une liste vide.
    similar = recommendations_map.get(str(movie_id), [])
 
    if not similar: #si la liste des films similaires est vide, on retourne une erreur 404 pour indiquer que le movieId n'est pas trouvé ou qu'il n'a pas de recommandations
        return {
            "movieId": movie_id,
            "similar": []
        }
 
    return {
        "movieId": movie_id,
        "similar": similar
    }

# if __name__ == "__main__":
#     # Test local du handler avec un event de test
#     test_event = {
#         "arguments": {"movieId": "3635"}
#     }
#     print(handler(test_event, None))