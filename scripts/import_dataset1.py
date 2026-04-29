import pandas as pd # pour lire les CSV
import boto3 # pour se connecter à AWS DynamoDB
import ast # pour convertir les strings de listes en vraies listes
from decimal import Decimal # pour convertir les floats en Decimal (DynamoDB n'accepte pas les floats)
from datetime import datetime, timezone # pour générer les timestamps createdAt et updatedAt
 
 
# CONNEXION À AWS DYNAMODB
 
 
print("Connexion à AWS...")
session = boto3.Session(profile_name='Recomodo-AdminAccess-Amplify-080941085602')
dynamodb = session.resource('dynamodb', region_name='eu-west-3')
 
NOM_TABLE_MOVIE = 'Movie-ijhwxiff7nbgfe7pbxjat2dtxi-NONE'
NOM_TABLE_GENRE = 'Genre-ijhwxiff7nbgfe7pbxjat2dtxi-NONE'
 
table_movie = dynamodb.Table(NOM_TABLE_MOVIE)
table_genre = dynamodb.Table(NOM_TABLE_GENRE)
 
# Timestamp actuel au format ISO 8601 (requis par Amplify/GraphQL)
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
 
 
# SUPPRESSION DE LA TABLE MOVIE
 
 
print("\nSuppression de tous les films existants...")
 
items_to_delete = []
response = table_movie.scan(ProjectionExpression="id")
items_to_delete.extend(response["Items"])
 
while "LastEvaluatedKey" in response:
    response = table_movie.scan(
        ProjectionExpression="id",
        ExclusiveStartKey=response["LastEvaluatedKey"]
    )
    items_to_delete.extend(response["Items"])
 
print(f"  {len(items_to_delete)} film(s) trouvé(s) à supprimer.")
 
with table_movie.batch_writer() as batch:
    for item in items_to_delete:
        batch.delete_item(Key={"id": item["id"]})
 
print("  Table Movie vidée.")
 
 
# SUPPRESSION DE LA TABLE GENRE
 
 
print("\nSuppression de tous les genres existants...")
 
items_to_delete_genre = []
response_genre = table_genre.scan(ProjectionExpression="id")
items_to_delete_genre.extend(response_genre["Items"])
 
while "LastEvaluatedKey" in response_genre:
    response_genre = table_genre.scan(
        ProjectionExpression="id",
        ExclusiveStartKey=response_genre["LastEvaluatedKey"]
    )
    items_to_delete_genre.extend(response_genre["Items"])
 
print(f"  {len(items_to_delete_genre)} genre(s) trouvé(s) à supprimer.")
 
with table_genre.batch_writer() as batch:
    for item in items_to_delete_genre:
        batch.delete_item(Key={"id": item["id"]})
 
print("  Table Genre vidée.")
 
 
# IMPORT TABLE GENRE
 
 
genres = pd.read_csv('scripts/dataset/genres_clean.csv')
 
print("\nImport des genres...")
 
errors_genres = 0
 
for index, row in genres.iterrows():
    try:
        table_genre.put_item(
            Item={
                'id': str(row['genreId']),
                'genreId': int(row['genreId']),
                'name': str(row['name']),
                'createdAt': now,  # ajout manuellement des timestamps
                'updatedAt': now,  
            }
        )
    except Exception as e:
        print(f"  Erreur sur le genre {row['name']} : {e}")
        errors_genres += 1
 
print(f"  Genres importés : {len(genres) - errors_genres}")
 
 
# IMPORT DE LA TABLE MOVIE
 
 
print("\nImport des films...")
 
print(f"Lecture du fichier des films depuis le CSV")
movies = pd.read_csv('scripts/dataset/movies_cleaned.csv')
print(f"{len(movies)} films à importer")
 
errors_movies = 0
 
for index, row in movies.iterrows():
    try:
        table_movie.put_item(
            Item={
                # Clé principale
                'id': str(row['movieId']),
 
                # Informations du film
                'movieId': str(row['movieId']),

                'title': str(row['title']),

                'titlelower': str(row['title']).lower(), # titre en minuscules
                
                'overview': str(row['overview']),
 
                # Reconvertit "[28, 16]" en vraie liste [28, 16]
                'genres': ast.literal_eval(str(row['genres'])),

                'mainGenre': int(ast.literal_eval(str(row['genres']))[0]),
 
                # Mots clés pour TF-IDF
                'keywords': str(row['keywords']),
 
                # Date de sortie
                'releaseDate': str(row['releaseDate']),
 
                # Note moyenne (Decimal car DynamoDB n'accepte pas float)
                'voteAverage': Decimal(str(row['voteAverage'])),
 
                # Nombre de votes
                'voteCount': int(row['voteCount']),
 
                # Réalisateur
                'director': str(row['director']) ,
 
                # Chemin affiche
                # URL complète = https://image.tmdb.org/t/p/w500 + posterPath
                'posterPath': str(row['posterPath']),

                'runtime': int(row['runtime']),

                'cast': str(row['cast']),
 
                'createdAt': now,  # ajout manuellement des timestamps
                'updatedAt': now,  
            }
        )
 
        # Afficher la progression toutes les 500 lignes
        if index % 500 == 0:
            print(f"  {index}/{len(movies)} films importés...")
 
    except Exception as e:
        print(f"  Erreur sur le film {row['title']} : {e}")
        errors_movies += 1
 
 
 
 
print(f"\n Import terminé !")
print(f"  Films importés  : {len(movies) - errors_movies}")
print(f"  Genres importés : {len(genres) - errors_genres}")
print(f"  Erreurs films   : {errors_movies}")
print(f"  Erreurs genres  : {errors_genres}")