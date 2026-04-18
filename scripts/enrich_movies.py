import pandas as pd
import ast

movies = pd.read_csv('scripts/dataset/movies_cleaned.csv')

metadata = pd.read_csv('scripts/dataset/movies_metadata.csv', low_memory=False)
credits = pd.read_csv('scripts/dataset/credits.csv')

#RUNTIME
metadata = metadata[['id', 'runtime']].copy()
metadata.rename(columns={'id': 'movieId'}, inplace=True)
metadata['movieId'] = pd.to_numeric(metadata['movieId'], errors='coerce')
metadata = metadata.dropna(subset=['movieId'])
metadata['movieId'] = metadata['movieId'].astype(int).astype(str)
metadata['runtime'] = pd.to_numeric(metadata['runtime'], errors='coerce')

# CAST (top 5 acteurs)
def extract_cast(cast_str, top_n=5):
    try:
        cast_list = ast.literal_eval(cast_str)
        names = [member['name'] for member in cast_list[:top_n]]
        return ', '.join(names)
    except:
        return None

credits = credits[['id', 'cast']].copy()
credits.rename(columns={'id': 'movieId'}, inplace=True)
credits['movieId'] = credits['movieId'].astype(str)
credits['cast'] = credits['cast'].apply(extract_cast)

# FUSION
movies['movieId'] = movies['movieId'].astype(str)
movies = movies.merge(metadata, on='movieId', how='left')
movies = movies.merge(credits, on='movieId', how='left')

# SUPPRESSION DES FILMS INCOMPLETS (sans runtime ou cast)
before = len(movies)

incomplete = movies[
    movies['runtime'].isna() | (movies['runtime'] <= 0) |
    movies['cast'].isna()    | (movies['cast'] == '')
]

# Export des IDs à supprimer dans DynamoDB
ids_to_delete = incomplete['movieId'].drop_duplicates()
ids_to_delete.to_csv('scripts/dataset/ids_to_delete.csv', index=False, header=True)
print(f"  {len(ids_to_delete)} films incomplets → IDs exportés dans ids_to_delete.csv")

# Suppression dans le csv 
movies = movies[~movies['movieId'].isin(ids_to_delete)]
movies['runtime'] = movies['runtime'].astype(int)

after = len(movies)
print(f"  {before - after} films supprimés de movies_cleaned.csv")

# SAUVEGARDE
movies.to_csv('scripts/dataset/movies_cleaned.csv', index=False)
print(f"Done ! {after} films enrichis avec runtime et cast.")