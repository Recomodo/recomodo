import json
import os
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key
 
dynamodb = boto3.resource("dynamodb")
 
MOVIE_TABLE_NAME = os.environ.get("MOVIE_TABLE_NAME")
MOVIE_MAIN_GENRE_INDEX = os.environ.get("MOVIE_MAIN_GENRE_INDEX")
 

# Fonction pour extraire les arguments de l'event, en gérant les deux cas possibles (arguments à la racine ou dans une clé "arguments")
def extract_arguments(event):
    if "arguments" in event:
        return event["arguments"]
    return event
 
 
def handler(event, context):
    # Le front envoie : {"genreId": 28, "excludedIds": ["123", "456", ...]}
    args = extract_arguments(event)
 
    genre_id = args.get("genreId")
    excluded_ids = args.get("excludedIds", [])
 
    if genre_id is None:
        raise ValueError("genreId est requis")
 
    movie_table = dynamodb.Table(MOVIE_TABLE_NAME)
 
    # On récupère les meilleurs films du genre directement
    response = movie_table.query(
        IndexName=MOVIE_MAIN_GENRE_INDEX,
        KeyConditionExpression=Key("mainGenre").eq(int(genre_id)),
        ScanIndexForward=False,  # tri décroissant sur le sort key (voteAverage)
        Limit=50,  # on prend les 50 meilleurs films du genre pour avoir assez de candidats
    )
 
    items = response.get("Items", [])
 
    # On filtre les films déjà affichés ou notés par l'utilisateur
    excluded_set = set(excluded_ids)
    candidates = [movie for movie in items if movie.get("movieId") not in excluded_set]
 
    if not candidates:
        return {
            "movieId": None,
            "message": f"Aucun film disponible pour le genre {genre_id}"
        }
 
    # On retourne le meilleur film disponible 
    best_movie = candidates[0]
 
    return {
        "movieId": best_movie.get("movieId"),
        "title": best_movie.get("title"),
        "posterPath": best_movie.get("posterPath"),
        "voteAverage": str(best_movie.get("voteAverage", "")),
        "genres": best_movie.get("genres", []),
        "mainGenre": int(best_movie.get("mainGenre", genre_id)),
        "overview": best_movie.get("overview", ""),
    }
 