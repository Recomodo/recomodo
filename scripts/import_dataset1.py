import pandas as pd # pour lire les CSV
import boto3 # pour se connecter à AWS DynamoDB
import os # pour accéder aux variables d'environnement AWS_ACCESS_KEY_ID et AWS_SECRET_ACCESS_KEY
import ast # pour convertir les strings de listes en vraies listes
from decimal import Decimal # pour convertir les floats en Decimal (DynamoDB n'accepte pas les floats)

# ============================================
# CONNEXION À AWS DYNAMODB
# ============================================

print("Connexion à AWS...")
#dynamodb = boto3.resource(
#    'dynamodb',
#    region_name='eu-west-3',
#    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
#    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
#)
session = boto3.Session(profile_name='Recomodo-AdminAccess-Amplify-080941085602')
dynamodb = session.resource('dynamodb', region_name='eu-west-3')


NOM_TABLE_MOVIE = 'Movie-pmu5tm5u2vfw5gpeaqtiqqs2be-NONE'#nom de la table DynamoDB pour les films
NOM_TABLE_GENRE = 'Genre-pmu5tm5u2vfw5gpeaqtiqqs2be-NONE'#nom de la table DynamoDB pour les genres

table_movie = dynamodb.Table(NOM_TABLE_MOVIE)

# ============================================
# IMPORT DE LA TABLE GENRE
# ============================================

# BUCKET = 'amplify-recomodo-nganzu-s-amplifydataamplifycodege-ans5kerozkaz'

# ============================================
# IMPORT DE LA TABLE MOVIE
# ============================================

print("\nImport des films...")

print(f"Lecture du fichier des films depuis le CSV")
#movies = pd.read_csv(f's3://{BUCKET}/dataset/movies_clean.csv') #pour lire depuis S3, sinon : "scripts/dataset/movies_clean.csv"
movies = pd.read_csv('scripts/dataset/movies_clean.csv')#pour lire depuis S3, sinon : "scripts/dataset/movies_clean.csv"
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

# ============================================
# RÉSULTAT FINAL
# ============================================

print(f"\n Import terminé !")
print(f" Films importés  : {len(movies) - errors_movies}")
print(f" Erreurs films   : {errors_movies}")