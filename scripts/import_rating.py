import pandas as pd
import boto3
import uuid
from decimal import Decimal
 

# CONNEXION À AWS DYNAMODB
 
print("Connexion à AWS...")
 
session = boto3.Session(profile_name='Recomodo-AdminAccess-Amplify-080941085602')
dynamodb = session.resource('dynamodb', region_name='eu-west-3')
 
NOM_TABLE_RATING = 'Rating-pmu5tm5u2vfw5gpeaqtiqqs2be-NONE'  # À adapter si besoin
 
table_rating = dynamodb.Table(NOM_TABLE_RATING)
 
# CHARGEMENT DU FICHIER RATINGS
# The Movies Dataset contient deux fichiers de ratings :
#   - ratings.csv       : ~26 millions de lignes (très lourd)
#   - ratings_small.csv : ~100 000 lignes (celui utilisé pour tester l'algorithme))
#
# Colonnes du fichier : userId, movieId, rating, timestamp
# Note : les userId sont des entiers anonymisés (pas des Cognito IDs)
# On les préfixe avec "tmdb_" pour les distinguer des vrais users
 # SUPPRESSION DE TOUS LES RATINGS EXISTANTS
print("\nSuppression de tous les ratings existants...")

items_to_delete = []
response = table_rating.scan(ProjectionExpression="id")
items_to_delete.extend(response["Items"])

while "LastEvaluatedKey" in response:
    response = table_rating.scan(
        ProjectionExpression="id",
        ExclusiveStartKey=response["LastEvaluatedKey"]
    )
    items_to_delete.extend(response["Items"])

print(f"  {len(items_to_delete)} rating(s) à supprimer.")

with table_rating.batch_writer() as batch: #batch_writer permet de faire des suppressions en lot, plus rapide que de supprimer un par un
    for item in items_to_delete:
        batch.delete_item(Key={"id": item["id"]})

print("  Table vidée.")


print("Lecture du fichier ratings...")
 
df = pd.read_csv('scripts/dataset/ratings_small.csv')
 
print(f"{len(df)} ratings à importer")
 
# FILTRAGE : garder uniquement les films
# qui existent dans notre table Movie nettoyée

 
movies = pd.read_csv('scripts/dataset/movies_cleaned.csv', usecols=['movieId']) #on ne charge que la colonne movieId pour gagner du temps et de la mémoire
movie_ids_valides = set(movies['movieId'].astype(str))#on convertit les movieId en string pour les comparer avec ceux du fichier ratings, qui sont aussi des string (car on les a convertis en string dans le script de nettoyage et dans Amplify)
 
df['movieId'] = df['movieId'].astype(str)#on convertit les movieId en string pour les comparer avec ceux du fichier movies_cleaned.csv, qui sont aussi des string (car on les a convertis en string dans le script de nettoyage et dans Amplify)
df = df[df['movieId'].isin(movie_ids_valides)]#on garde uniquement les ratings dont le movieId est dans la liste des movieId valides (ceux de movies_cleaned.csv)
 
print(f"{len(df)} ratings après filtrage sur les films existants")
 

# IMPORT DANS DYNAMODB
 
errors = 0
 
print("\nImport des ratings...")
 
with table_rating.batch_writer() as batch:
    for index, row in df.iterrows():
        try:
            batch.put_item(
                Item={
                    # Clé primaire générée par Amplify
                    'id': str(uuid.uuid4()),
 
                    # userId préfixé pour distinguer les users TMDB
                    # des vrais utilisateurs Cognito
                    'userId': f"tmdb_{int(row['userId'])}",
 
                    # movieId du film noté
                    'movieId': str(row['movieId']),
 
                    # Note entre 0.5 et 5.0 dans le fichier ratings, on la convertit en float et on la multiplie par 2 pour avoir une échelle de 0 à 10, cohérente avec les notes affichées sur l'application et le dataset movies_cleaned.csv
                    # (on la convertit en Decimal car DynamoDB refuse les floats)
                    'rating': Decimal(str(round(float(row['rating'])*2, 1))), # on multiplie par 2 pour avoir une échelle de 0 à 10, pour être cohérent avec les notes affichées sur l'application et le dataset movies_cleaned.csv
 
                    # Champs Amplify obligatoires pour allow.owner()
                    # On simule un owner cohérent avec le userId
                    'owner': f"tmdb_{int(row['userId'])}",
                }
            )
 
            if index % 1000 == 0:
                print(f"  {index}/{len(df)} ratings importés...")
 
        except Exception as e:
            print(f"  Erreur ligne {index} : {e}")
            errors += 1
 
# RÉSULTAT FINAL
 
print(f"\nImport terminé !")
print(f"  Ratings importés : {len(df) - errors}")
print(f"  Erreurs          : {errors}")