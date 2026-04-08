import json
import os
import boto3

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd

MOVIES_COLLECTION = "Movie-pmu5tm5u2vfw5gpeaqtiqqs2be-NONE"
GENRES_COLLECTION = "Genre-pmu5tm5u2vfw5gpeaqtiqqs2be-NONE"

dynamodb = boto3.resource("dynamodb")
movies_table = dynamodb.Table("Movie-pmu5tm5u2vfw5gpeaqtiqqs2be-NONE")
#genres_table = dynamodb.Table(GENRES_COLLECTION)

def handler(event, context):
    response = movies_table.scan()

    movies = response.get("Items", [])

    return {
        "statusCode": 200,
        "body": json.dumps({
            "count": len(movies),
            "movies": movies
        })
    }

response = movies_table.scan()
movies = response.get("Items", [])

single_movie_response = movies_table.get_item(
    Key={"id": "5"}
)
movie = single_movie_response.get("Item")

print("affichage un film :") 
print(movie)
