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
# 3. Supprime les films avec moins de 5 votes
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

movies = pd.read_csv(
    "data/dataset/movies_metadata.csv",
    low_memory=False  # évite les warnings liés aux types mélangés
)

keywords = pd.read_csv("data/dataset/keywords.csv")
credits = pd.read_csv("data/dataset/credits.csv")

print(f"Nombre total de films chargés : {len(movies)}")


# ==========================================================
# NETTOYAGE DU FICHIER movies_metadata.csv
# ==========================================================

print("\nNettoyage des films...")

# Colonnes utiles pour notre projet
movies = movies[[
    "id",
    "title",
    "overview",
    "genres",
    "release_date",
    "vote_average",
    "vote_count",
    "poster_path"
]]

# Suppression des films sans titre ou résumé
movies = movies.dropna(subset=["title", "overview"])

# Suppression des films avec moins de 5 votes
movies = movies[movies["vote_count"] >= 5]

# Suppression des IDs mal formatés (certains ne sont pas numériques)
movies = movies[movies["id"].apply(lambda x: str(x).isdigit())]

# Conversion des IDs en string (car movieId est a.string() dans Amplify)
movies["id"] = movies["id"].astype(str)


# ==========================================================
# 3. EXTRACTION DES IDS DE GENRES
# ==========================================================
# On transforme :
# "[{'id': 28, 'name': 'Action'}]"
# en :
# [28]

def extraire_ids_genres(chaine):
    try:
        liste = ast.literal_eval(chaine)
        return [genre["id"] for genre in liste]
    except:
        return []

movies["genres"] = movies["genres"].apply(extraire_ids_genres)


# ==========================================================
# 4. EXTRACTION DES KEYWORDS
# ==========================================================
# On transforme la liste JSON en string :
# "hero, space, war"

def extraire_keywords(chaine):
    try:
        liste = ast.literal_eval(chaine)
        return ", ".join([mot["name"] for mot in liste])
    except:
        return ""

keywords["id"] = keywords["id"].astype(str)
keywords["keywords"] = keywords["keywords"].apply(extraire_keywords)


# ==========================================================
# 5. EXTRACTION DU RÉALISATEUR
# ==========================================================

def extraire_realisateur(chaine):
    try:
        crew = ast.literal_eval(chaine)
        for membre in crew:
            if membre["job"] == "Director":
                return membre["name"]
    except:
        return ""
    return ""

credits["id"] = credits["id"].astype(str)
credits["director"] = credits["crew"].apply(extraire_realisateur)

credits = credits[["id", "director"]]


# ==========================================================
# 6. FUSION DES 3 FICHIERS
# ==========================================================

print("Fusion des fichiers...")

movies = movies.merge(keywords[["id", "keywords"]], on="id", how="left")
movies = movies.merge(credits, on="id", how="left")


# ==========================================================
# 7. RENOMMAGE DES COLONNES POUR CORRESPONDRE AU SCHÉMA
# ==========================================================

movies = movies.rename(columns={
    "id": "movieId",
    "release_date": "releaseDate",
    "vote_average": "voteAverage",
    "vote_count": "voteCount",
    "poster_path": "posterPath"
})


# ==========================================================
# 8. SÉLECTION DES COLONNES FINALES
# ==========================================================

movies = movies[[
    "movieId",
    "title",
    "overview",
    "genres",        # tableau d'entiers
    "keywords",
    "releaseDate",
    "voteAverage",
    "voteCount",
    "posterPath",
    "director"
]]


# ==========================================================
# 9. SAUVEGARDE DE LA TABLE MOVIE
# ==========================================================

movies.to_csv(
    "data/dataset/movies_cleaned.csv",
    index=False
)

print(f"Nombre final de films : {len(movies)}")
print("Fichier movies_cleaned.csv généré avec succès.")


# ==========================================================
# 10. GÉNÉRATION DE LA TABLE GENRE
# ==========================================================

print("\nGénération de la table Genre...")

genres_dict = {}

for liste in movies["genres"]:
    for gid in liste:
        genres_dict[gid] = None

# On récupère les noms depuis le dataset original
for _, row in pd.read_csv(
    "data/dataset/movies_metadata.csv",
    low_memory=False
).iterrows():
    try:
        liste = ast.literal_eval(row["genres"])
        for genre in liste:
            if genre["id"] in genres_dict:
                genres_dict[genre["id"]] = genre["name"]
    except:
        continue

genre_df = pd.DataFrame([
    {"genreId": gid, "name": name}
    for gid, name in genres_dict.items()
    if name is not None
])

genre_df.to_csv(
    "data/dataset/genres_clean.csv",
    index=False
)

print("Fichier genres_clean.csv généré avec succès.")
print("\n Script terminé correctement.")