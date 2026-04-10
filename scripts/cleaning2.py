# Renettoyage du dataset movies_clean.csv
# erreur lors du premier nettoyage : certains films avaient des genres vides (ex: "genres": "[]") , des keywords vides (ex: "keywords": "") ou ils étaient en double (probablement à cause de l'ajout de la colonne keywords)
import pandas as pd
import ast

print("Chargement de movies_clean.csv...")

movies = pd.read_csv("scripts/dataset/movies_clean.csv")

nombre_initial = len(movies)
print(f"Nombre initial de films : {nombre_initial}")

#Suprression des doublons (certains films étaient présents plusieurs fois, probablement à cause de l'ajout de la colonne keywords)
print("\nSuppression des doublons...")

avant_doublons = len(movies)

movies = movies.drop_duplicates(subset=["movieId"])

apres_doublons = len(movies)
doublons_supprimes = avant_doublons - apres_doublons

print(f"Doublons supprimés : {doublons_supprimes}")

# Nettoyage des genres vides
# Les genres sont stockés sous forme de string "[28, 12]"
# On doit les reconvertir en liste pour vérifier si vide

def est_genre_vide(chaine):
    try:
        liste = ast.literal_eval(chaine) # reconvertit la string en liste
        return len(liste) == 0
    except:
        return True  # si erreur → on considère comme vide

mask_genres_vides = movies["genres"].apply(est_genre_vide)# masque de True/False pour les genres vides

films_genres_vides = mask_genres_vides.sum() # Compte le nombre de True dans le masque, soit le nombre de films avec genres vides

movies = movies[~mask_genres_vides] # On garde que les films dont le masque est False (genres non vides)


# 2. Suppression des keywords vides

films_keywords_vides = movies["keywords"].isna().sum() + (movies["keywords"] == "").sum()

movies = movies[movies["keywords"].notna()]
movies = movies[movies["keywords"] != ""]

# 5. SUPPRESSION DES FILMS INCOMPLETS (avec d'autres données manquantes)
print("\nSuppression des films avec données manquantes...")

avant_filtrage = len(movies)

# Supprime toute ligne avec au moins un NaN dans n'importe quelle colonne
movies = movies.dropna()

# Supprime aussi les chaînes vides "" dans tout le dataset
movies = movies[~(movies == "").any(axis=1)]

apres_filtrage = len(movies)

films_incomplets = avant_filtrage - apres_filtrage

print(f"Films incomplets supprimés : {films_incomplets}")

nombre_final = len(movies)
films_supprimes = nombre_initial - nombre_final

print("\n======== RÉSUMÉ ========")
print(f"Films avec genres vides supprimés : {films_genres_vides}")
print(f"Films avec keywords vides supprimés : {films_keywords_vides}")
print(f"Total supprimés : {films_supprimes}")
print(f"Nombre final de films : {nombre_final}")



# Sauvegarde

movies.to_csv("scripts/dataset/movies_cleaned.csv", index=False)

print("\nFichier movies_cleaned.csv généré avec succès.")
print("Script terminé correctement.")