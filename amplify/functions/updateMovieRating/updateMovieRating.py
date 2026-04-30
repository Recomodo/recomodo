import json
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal

#session = boto3.Session(profile_name="Recomodo-AdminAccess-Amplify-080941085602") #configuration de la session boto3 pour accéder à DynamoDB, à remplacer par boto3 directement en prod

dynamodb = boto3.resource("dynamodb")

RATING_TABLE_NAME = os.environ.get("RATING_TABLE_NAME")
MOVIE_TABLE_NAME = os.environ.get("MOVIE_TABLE_NAME")
RATING_USER_ID_INDEX = os.environ.get("RATING_USER_ID_INDEX")
RATING_MOVIE_ID_INDEX = os.environ.get("RATING_MOVIE_ID_INDEX")
MOVIE_MOVIE_ID_INDEX = os.environ.get("MOVIE_MOVIE_ID_INDEX")

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

    #/////////////
    print("EVENT =", event)
    print("ARGS =", args)
    print("user_id =", user_id, type(user_id))
    print("movie_id =", movie_id, type(movie_id))
    print("rating_value =", rating_value, type(rating_value))
    print("RATING_TABLE_NAME =", RATING_TABLE_NAME)
    print("MOVIE_TABLE_NAME =", MOVIE_TABLE_NAME)
    print("RATING_USER_ID_INDEX =", RATING_USER_ID_INDEX)
    print("RATING_MOVIE_ID_INDEX =", RATING_MOVIE_ID_INDEX)
    print("MOVIE_MOVIE_ID_INDEX =", MOVIE_MOVIE_ID_INDEX)
    #///////////

    # Validation des arguments si un d'eux est manquant, on retourne une erreur
    if not user_id or not movie_id or rating_value is None:
        raise ValueError("userId, movieId et rating sont requis")

    rating_table = dynamodb.Table(RATING_TABLE_NAME)
    movie_table = dynamodb.Table(MOVIE_TABLE_NAME)

    # Créer ou mettre à jour le Rating de cet utilisateur 

    # On cherche si ce user a déjà noté ce film via une query
    user_rating = query_all_items(
        rating_table,
        RATING_USER_ID_INDEX,
        Key("userId").eq(user_id)
    )

    existing = [item for item in user_rating if item["movieId"] == movie_id]

    if existing:
        # Mise à jour de la note existante si l'utilisateur a déjà noté ce film
        item = existing[0]
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
    
    #//////
    print("NOTE ENREGISTREE POUR movie_id =", movie_id)
    print("existing =", existing)
    #//////

    #récupérer tous les ratings de ce film pour recalculer la moyenne et le nombre de votes
    all_ratings = query_all_items(
        rating_table,
        RATING_MOVIE_ID_INDEX,
        Key("movieId").eq(movie_id)
    )

    #//////
    print("QUERY ALL RATINGS movie_id =", movie_id, type(movie_id))
    print("all_ratings =", all_ratings)
    print("len(all_ratings) =", len(all_ratings))
    #//////

    #Trouver le film dans la table Movie
    #on cherche avec le movieId et non l'id Dynamodb
    movies = query_all_items(
        movie_table,
        MOVIE_MOVIE_ID_INDEX,
        Key("movieId").eq(movie_id)
    )

    #//////
    print("movies =", movies)
    print("len(movies) =", len(movies))
    #//////

    if not movies:
        return {"success": False, "message": f"Film {movie_id} introuvable"}

    movie = movies[0]

    #calculer la nouvelle moyenne et le nombre de votes à partir de tous les ratings de ce film
    rating_values = [float(r["rating"]) for r in all_ratings]
    vote_count = len(rating_values)
    vote_average = round(sum(rating_values) / vote_count, 1) if vote_count > 0 else 0.0

    # initial_vote_count = int(movie.get("initialVoteCount") or movie.get("voteCount") or 0)
    # initial_vote_average = float(movie.get("initialVoteAverage") or movie.get("voteAverage") or 0.0)

    # rating_values = [float(r["rating"]) for r in all_ratings]
    # user_vote_count = len(rating_values)
    # user_vote_sum = sum(rating_values)

    # total_count = initial_vote_count + user_vote_count
    # total_sum = (initial_vote_average * initial_vote_count) + user_vote_sum
    # vote_average = round(total_sum / total_count, 1) if total_count > 0 else 0.0

    # Mettre à jour voteAverage et voteCounT dans Movie 
    movie_table.update_item(
        Key={"id": movie["id"]},
        UpdateExpression="SET voteAverage = :avg, voteCount = :cnt", 
        ExpressionAttributeValues={
            ":avg": Decimal(str(vote_average)),
            ":cnt": vote_count,
        },
    )

    #//////
    print("rating_values =", rating_values)
    print("vote_count =", vote_count)
    print("vote_average =", vote_average)
    #//////

    return {"success": True, "message": "Note enregistrée et film mis à jour"}


# #si c'est la 1ère note pour ce film, on stocke aussi les valeurs initiales de voteAverage et voteCount
#     initial_vote_count = int(movie.get("initialVoteCount") or movie.get("voteCount") or 0)
#     initial_vote_average = float(movie.get("initialVoteAverage") or movie.get("voteAverage") or 0.0)


#     # Calculer la nouvelle moyenne en combinant dataset + utilisateurs 

#     rating_values = [float(r["rating"]) for r in all_ratings["Items"]]
#     user_vote_count = len(rating_values)
#     user_vote_sum = sum(rating_values)

#     total_count = initial_vote_count + user_vote_count
#     total_sum = (initial_vote_average * initial_vote_count) + user_vote_sum
#     vote_average = round(total_sum / total_count, 1) if total_count > 0 else 0.0



#     # Mettre à jour voteAverage et voteCounT dans Movie 
#     movie_table.update_item(
#         Key={"id": movie["id"]},
#         UpdateExpression="SET voteAverage = :avg, voteCount = :cnt, #iavg = :iavg, #icnt = :icnt",
#         ExpressionAttributeNames={
#             "#iavg": "initialVoteAverage",
#             "#icnt": "initialVoteCount",
#     },   
#         ExpressionAttributeValues={
#             ":avg": Decimal(str(vote_average)),
#             ":cnt": total_count,
#             ":iavg": Decimal(str(initial_vote_average)),
#             ":icnt": initial_vote_count,
#         },
#     )

#     return {"success": True, "message": "Note enregistrée et film mis à jour"}
if __name__ == "__main__":
    test_event = {
        "arguments": {
            "userId": "tmdb_430",
            "movieId": "587",
            "rating": 7.5
        }
    }

    print("===== TEST LOCAL updateMovieRating =====")
    print("RATING_TABLE_NAME =", RATING_TABLE_NAME)
    print("MOVIE_TABLE_NAME =", MOVIE_TABLE_NAME)
    print("RATING_USER_ID_INDEX =", RATING_USER_ID_INDEX)
    print("RATING_MOVIE_ID_INDEX =", RATING_MOVIE_ID_INDEX)
    print("MOVIE_MOVIE_ID_INDEX =", MOVIE_MOVIE_ID_INDEX)
    print("EVENT =", test_event)

    result = handler(test_event, None)
    print("RESULT =", result)
