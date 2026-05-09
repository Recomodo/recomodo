import os
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
from datetime import datetime, timezone


dynamodb = boto3.resource("dynamodb")

RATING_TABLE_NAME = os.environ.get("RATING_TABLE_NAME")
MOVIE_TABLE_NAME = os.environ.get("MOVIE_TABLE_NAME")
RATING_USER_ID_INDEX = os.environ.get("RATING_USER_ID_INDEX")
RATING_MOVIE_ID_INDEX = os.environ.get("RATING_MOVIE_ID_INDEX")
MOVIE_MOVIE_ID_INDEX = os.environ.get("MOVIE_MOVIE_ID_INDEX")

def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

#les arguments peuvent être à la racine de l'event ou dans une clé "arguments" 
# selon comment le front appelle le Lambda 
#cette fonction gère les deux cas
def extract_arguments(event):
    if "arguments" in event:
        return event["arguments"]
    return event

#fonction pour faire une query paginée sur DynamoDB, pour récupérer tous les items correspondant à une condition même s'il y en a plus de 1MB
def query_all_items(table, index_name, key_condition):
    items = []
    response = table.query(
        IndexName=index_name,
        KeyConditionExpression=key_condition
    )
    items.extend(response.get("Items", []))

    while "LastEvaluatedKey" in response:
        response = table.query(
            IndexName=index_name,
            KeyConditionExpression=key_condition,
            ExclusiveStartKey=response["LastEvaluatedKey"]
        )
        items.extend(response.get("Items", []))

    return items


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

    #Trouver le film dans la table Movie
    #on cherche avec le movieId et non l'id Dynamodb
    movies = query_all_items(
        movie_table,
        MOVIE_MOVIE_ID_INDEX,
        Key("movieId").eq(movie_id)
    )

    if not movies:
        return {"success": False, "message": f"Film {movie_id} introuvable"}

    movie = movies[0]

    #On récupère les valeurs de voteCount et voteAverage avant la mise à jour pour pouvoir les utiliser dans le calcul de la nouvelle moyenne et du nouveau nombre de votes
    base_vote_count = int(movie.get("initialVoteCount") or movie.get("voteCount") or 0)
    base_vote_average = float(movie.get("initialVoteAverage") or movie.get("voteAverage") or 0.0)


    # Créer ou mettre à jour le Rating de cet utilisateur 
    # On cherche si ce user a déjà noté ce film via une query
    user_ratings = query_all_items(
        rating_table,
        RATING_USER_ID_INDEX,
        Key("userId").eq(user_id)
    )

    existing = [item for item in user_ratings if item["movieId"] == movie_id]
    current_time = now_iso()

    if existing:
        # Mise à jour de la note existante si l'utilisateur a déjà noté ce film
        item = existing[0]
        rating_table.update_item(
            Key={"id": item["id"]},
            UpdateExpression="SET rating = :r, updatedAt = :u",
            ExpressionAttributeValues={
                ":r": Decimal(str(rating_value)),
                ":u": current_time
            }

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
                "createdAt": current_time,
                "updatedAt": current_time
            }
        )
    

    #récupérer tous les ratings de ce film pour recalculer la moyenne et le nombre de votes
    all_ratings = query_all_items(
        rating_table,
        RATING_MOVIE_ID_INDEX,
        Key("movieId").eq(movie_id)
    )

    
    rating_values = [float(r["rating"]) for r in all_ratings]
    user_vote_count = len(rating_values)
    user_vote_sum = sum(rating_values)

    # On combine les votes existants (base_vote_count et base_vote_average) avec les nouveaux votes
    total_count = base_vote_count + user_vote_count
    total_sum = (base_vote_average * base_vote_count) + user_vote_sum
    vote_average = round(total_sum / total_count, 1) if total_count > 0 else 0.0

    # Mettre à jour voteAverage et voteCount dans Movie 
    movie_table.update_item(
        Key={"id": movie["id"]},
        UpdateExpression="SET voteAverage = :avg, voteCount = :cnt, #iavg = :iavg, #icnt = :icnt, updatedAt = :u", 
        ExpressionAttributeNames={
            "#iavg": "initialVoteAverage",
            "#icnt": "initialVoteCount"
        },
        ExpressionAttributeValues={
            ":avg": Decimal(str(vote_average)),
            ":cnt": total_count,
            ":iavg": Decimal(str(base_vote_average)),
            ":icnt": base_vote_count,
            ":u": current_time
        },
    )

    return {"success": True, "message": "Note enregistrée et film mis à jour"}
