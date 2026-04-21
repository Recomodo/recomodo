import json
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")

RATING_TABLE_NAME = os.environ.get("RATING_TABLE_NAME")
MOVIE_TABLE_NAME = os.environ.get("MOVIE_TABLE_NAME")

#les arguments peuvent être à la racine de l'event ou dans une clé "arguments" 
# selon comment le front appelle le Lambda 
#cette fonction gère les deux cas
def extract_arguments(event):
    if "arguments" in event:
        return event["arguments"]
    return event

#fonction handler qui est appelée à chaque fois que le Lambda est invoqué
def handler(event, context):
    args = extract_arguments(event)

    user_id = args.get("userId")
    movie_id = args.get("movieId")
    rating_value = args.get("rating")

    # Validation des arguments si un d'eux est manquant, on retourne une erreur
    if not user_id or not movie_id or rating_value is None:
        raise ValueError("userId, movieId et rating sont requis")

    rating_table = dynamodb.Table(RATING_TABLE_NAME)
    movie_table = dynamodb.Table(MOVIE_TABLE_NAME)

    # Créer ou mettre à jour le Rating de cet utilisateur 

    # On cherche si ce user a déjà noté ce film via un scan filtré
    existing = rating_table.scan(
        FilterExpression=Attr("userId").eq(user_id) & Attr("movieId").eq(movie_id)
    )

    if existing["Items"]:
        # Mise à jour de la note existante si l'utilisateur a déjà noté ce film
        item = existing["Items"][0]
        rating_table.update_item(
            Key={"id": item["id"]},
            UpdateExpression="SET rating = :r",
            ExpressionAttributeValues={":r": Decimal(str(rating_value))},
        )
    else:
        # Sinon création d'une nouvelle note
        import uuid
        rating_table.put_item(
            Item={
                "id": str(uuid.uuid4()),
                "userId": user_id,
                "movieId": movie_id,
                "rating": Decimal(str(rating_value)),
                "owner": user_id,  # champ requis par Amplify pour allow.owner()
                "__typename": "Rating",
            }
        )

    # Recalculer voteAverage et voteCount pour ce film 

    all_ratings = rating_table.scan(
        FilterExpression=Attr("movieId").eq(movie_id)
    )

    rating_values = [float(r["rating"]) for r in all_ratings["Items"]]
    vote_count = len(rating_values)
    vote_average = round(sum(rating_values) / vote_count, 1) if vote_count > 0 else 0.0

    # Trouver le film dans la table Movie
    #on cherche avec le movieId et non l'id Dynamodb
    movies = movie_table.scan(
        FilterExpression=Attr("movieId").eq(movie_id)
    )

    if not movies["Items"]:
        return {"success": False, "message": f"Film {movie_id} introuvable"}

    movie = movies["Items"][0]

    #si c'est la 1ère note pour ce film, on stocke aussi les valeurs initiales de voteAverage et voteCount
    initial_vote_count = int(movie.get("initialVoteCount") or movie.get("voteCount") or 0)
    initial_vote_average = float(movie.get("initialVoteAverage") or movie.get("voteAverage") or 0.0)


    # Calculer la nouvelle moyenne en combinant dataset + utilisateurs 

    rating_values = [float(r["rating"]) for r in all_ratings["Items"]]
    user_vote_count = len(rating_values)
    user_vote_sum = sum(rating_values)

    total_count = initial_vote_count + user_vote_count
    total_sum = (initial_vote_average * initial_vote_count) + user_vote_sum
    vote_average = round(total_sum / total_count, 1) if total_count > 0 else 0.0



    # Mettre à jour voteAverage et voteCounT dans Movie 
    movie_table.update_item(
        Key={"id": movie["id"]},
        UpdateExpression="SET voteAverage = :avg, voteCount = :cnt, #iavg = :iavg, #icnt = :icnt",
        ExpressionAttributeNames={
            "#iavg": "initialVoteAverage",
            "#icnt": "initialVoteCount",
    },   
        ExpressionAttributeValues={
            ":avg": Decimal(str(vote_average)),
            ":cnt": total_count,
            ":iavg": Decimal(str(initial_vote_average)),
            ":icnt": initial_vote_count,
        },
    )

    return {"success": True, "message": "Note enregistrée et film mis à jour"}