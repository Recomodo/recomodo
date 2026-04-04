# PROMPT UTILISÉ POUR GÉNÉRER CE SCRIPT
# "Je développe un système de recommandation de films
# avec AWS Amplify Gen 2 et DynamoDB. J'utilise le dataset
# Kaggle 'The Movies Dataset' qui contient 3 fichiers CSV :
# movies_metadata.csv, keywords.csv et credits.csv.
# Je veux un script Python qui :
# 1. Charge les 3 fichiers CSV
# 2. Nettoie movies_metadata.csv en gardant seulement
#    les colonnes : id, title, overview, genres,
#    release_date, vote_average, vote_count, poster_path
# 3. Supprime les films avec moins de 50 votes
#    et les films sans titre ou résumé
# 4. Extrait les genres depuis le format JSON vers
#    une simple string ex: 'Action, Comedy'
# 5. Extrait les keywords depuis keywords.csv
#    dans le même format
# 6. Extrait le réalisateur depuis credits.csv
# 7. Fusionne les 3 fichiers sur la colonne id
# 8. Renomme les colonnes pour correspondre
#    au schéma DynamoDB du projet
# 9. Sauvegarde le résultat en CSV "
import pandas as pd
import ast
# ============================================
# CHARGEMENT DES 3 FICHIERS CSV
# ============================================

print("Chargement des fichiers...")

films = pd.read_csv('scripts/dataset/movies_metadata.csv', low_memory=False) # ce fichier est énorme, on met low_memory=False pour éviter les warnings de types mélangés
keywords = pd.read_csv('scripts/dataset/keywords.csv')
credits = pd.read_csv('scripts/dataset/credits.csv')

print(f"Films chargés : {len(films)}")
print(f"Keywords chargés : {len(keywords)}")
print(f"Credits chargés : {len(credits)}")

# ============================================
# NETTOYAGE DE movies_metadata.csv
# ============================================

print("\nNettoyage des films...")

# Garder seulement les colonnes utiles
films = films[[
    'id', 'title', 'overview', 'genres',
    'release_date', 'vote_average',
    'vote_count', 'poster_path'
]]

# Supprimer les films sans titre ou sans résumé
films = films.dropna(subset=['title', 'overview'])

# Garder seulement les films avec assez de votes
# (évite les films inconnus avec fausse bonne note)
films = films[films['vote_count'] >= 5]

# Nettoyer les IDs mal formatés
# (ce dataset a des IDs bizarres parfois)
films = films[films['id'].apply(lambda x: str(x).isdigit())]
films['id'] = films['id'].astype(int)

# Extraire l'année depuis la date de sortie
films['annee'] = pd.to_datetime(
    films['release_date'], errors='coerce'
).dt.year.astype('Int64').astype(str)

# ============================================
# NETTOYAGE DES GENRES
# Dans le dataset les genres sont stockés comme ça :
# "[{'id': 28, 'name': 'Action'}, {'id': 12, 'name': 'Adventure'}]"
# On veut juste : "Action, Adventure"
# ============================================

def extraire_noms(chaine):
    try:
        liste = ast.literal_eval(chaine)
        return ', '.join([x['name'] for x in liste])# si la chaîne est vide ou mal formée, on retourne une chaîne vide
    except:
        return ''

films['genres'] = films['genres'].apply(extraire_noms)

# ============================================
# NETTOYAGE DE keywords.csv
# Même format bizarre que les genres
# ============================================

print("Nettoyage des keywords...")

keywords['id'] = keywords['id'].astype(int)
keywords['keywords'] = keywords['keywords'].apply(extraire_noms)

# ============================================
# NETTOYAGE DE credits.csv
# On extrait seulement le réalisateur
# ============================================

print("Nettoyage des credits...")

credits['id'] = credits['id'].astype(int)

# Extraire le réalisateur depuis la colonne "crew"
def extraire_realisateur(crew_str):
    try:
        crew = ast.literal_eval(crew_str)
        for membre in crew:
            if membre['job'] == 'Director':
                return membre['name']
    except:
        return ''
    return ''

credits['director'] = credits['crew'].apply(extraire_realisateur)

# Garder seulement les colonnes utiles
credits = credits[['id', 'director']]

# ============================================
# FUSIONNER LES 3 FICHIERS
# ============================================

print("\nFusion des fichiers...")

# Fusionner films avec keywords
films = films.merge(keywords, on='id', how='left')

# Fusionner avec credits
films = films.merge(credits, on='id', how='left')

# Renommer les colonnes pour correspondre
# à votre table DynamoDB
films = films.rename(columns={
    'id': 'movieId',
    'title': 'title',
    'overview': 'overview',
    'genres': 'genres',
    'keywords': 'keywords',
    'vote_average': 'voteAverage',
    'vote_count': 'voteCount',
    'poster_path': 'posterPath',
    'director': 'director'
})

# Garder seulement les colonnes finales
films = films[[
    'movieId', 'title', 'overview', 'genres',
    'keywords', 'annee', 'voteAverage',
    'voteCount', 'posterPath', 'director'
]]

# ============================================
# SAUVEGARDER LE FICHIER NETTOYÉ
# ============================================

films.to_csv('scripts/dataset/films_nettoyes.csv', index=False)

print(f"\n Films après nettoyage : {len(films)}")
print(" Fichier sauvegardé : scripts/dataset/films_nettoyes.csv")