import pandas as pd # pour lire les CSV
import boto3 # pour se connecter à AWS DynamoDB
import os #pour accéder aux variables d'environnement AWS_ACCESS_KEY_ID et AWS_SECRET_ACCESS_KEY
import ast # pour convertir les strings de listes en vraies listes
from decimal import Decimal # pour convertir les floats en Decimal (DynamoDB n'accepte pas les floats)


# CONNEXION À AWS DYNAMODB


print("Connexion à AWS...")
#dynamodb = boto3.resource(
#   'dynamodb',
#   region_name='eu-west-3',
#   aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
#   aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
#)
session = boto3.Session(profile_name='Recomodo-AdminAccess-Amplify-080941085602')
dynamodb = session.resource('dynamodb', region_name='eu-west-3')


NOM_TABLE_MOVIE = 'Movie-plmvpye27falferla5jpy5hchi-NONE'#nom de la table DynamoDB pour les films
NOM_TABLE_GENRE = 'Genre-plmvpye27falferla5jpy5hchi-NONE'#nom de la table DynamoDB pour les genres

table_movie = dynamodb.Table(NOM_TABLE_MOVIE)
table_genre = dynamodb.Table(NOM_TABLE_GENRE)

#Supression de la table Movie (pour repartir de zéro à chaque fois, pour éviter les doublons à chaque import)
print(f"Suppression de la table {NOM_TABLE_MOVIE} (si elle existe)...")
scan = table_movie.scan(ProjectionExpression="id")

with table_movie.batch_writer() as batch:
    for item in scan["Items"]:
        batch.delete_item(Key={"id": item["id"]})

print("Table vidée.")

#IMPORT TABLE GENRE
# Lecture du fichier des genres
genres = pd.read_csv(f'scripts/dataset/genres_clean.csv')
print("\nImport des genres...")

# Compteur d'erreurs pour le rapport final
errors_genres = 0

# On parcourt chaque ligne du CSV des genres
for index, row in genres.iterrows():
    try:
        # put_item envoie un enregistrement dans DynamoDB
        table_genre.put_item(
            Item={
                # 'id' est la clé principale générée par Amplify
                # elle doit être unique pour chaque genre
                'id': str(row['genreId']),

                # genreId : l'ID du genre depuis le dataset TMDB
                # ex: 28 pour Action, 16 pour Animation
                'genreId': int(row['genreId']),

                # name : le nom du genre
                # ex: "Action", "Animation", "Comedy"
                'name': str(row['name']),
            }
        )
    except Exception as e:
        # Si une erreur arrive on l'affiche et on continue
         print(f" Erreur sur le genre {row['name']} : {e}")
         errors_genres += 1

print(f" Genres importés : {len(genres) - errors_genres}")



 #IMPORT DE LA TABLE MOVIE


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
                'overview': str(row['overview']),

                # Reconvertit "[28, 16]" en vraie liste [28, 16]
                'genres': ast.literal_eval(str(row['genres'])),

                # Mots clés pour TF-IDF
                'keywords': str(row['keywords']) if pd.notna(row['keywords']) else '',

                # Date de sortie
                'releaseDate': str(row['releaseDate']) if pd.notna(row['releaseDate']) else '',

                # Note moyenne (Decimal car DynamoDB n'accepte pas float)
                'voteAverage': Decimal(str(row['voteAverage'])),

                # Nombre de votes
                'voteCount': int(row['voteCount']),

                # Réalisateur
                'director': str(row['director']) if pd.notna(row['director']) else '',

                # Chemin affiche
                # URL complète = https://image.tmdb.org/t/p/w500 + posterPath
                'posterPath': str(row['posterPath']) if pd.notna(row['posterPath']) else '',
            }
        )

        # Afficher la progression toutes les 500 lignes
        if index % 500 == 0:
            print(f" {index}/{len(movies)} films importés...")

    except Exception as e:
        print(f" Erreur sur le film {row['title']} : {e}")
        errors_movies += 1


# RÉSULTAT FINAL


print(f"\n Import terminé !")
print(f" Films importés  : {len(movies) - errors_movies}")
print(f" Genres importés : {len(genres) - errors_genres}")
print(f" Erreurs films   : {errors_movies}")
print(f" Erreurs genres  : {errors_genres}")