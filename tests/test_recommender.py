# Ce script se lance avec pytest tests/test_recommender.py -v

import os
import json
import pytest
import sys
from pathlib import Path

#Variables d'environnement minimales pour permettre l'import de recommender.py
os.environ.setdefault("AWS_DEFAULT_REGION", "eu-west-3")
os.environ.setdefault("RATINGS_TABLE_NAME", "dummy-ratings-table")
os.environ.setdefault("RATINGS_USER_ID_INDEX", "dummy-user-index")
os.environ.setdefault("DATA_BUCKET_NAME", "dummy-bucket")
os.environ.setdefault("MOVIES_RECOMMENDATIONS_KEY", "dummy-key")

#Chemin vers le dossier contenant recommender.py
LAMBDA_DIR = Path("amplify/functions/recommender").resolve()
if str(LAMBDA_DIR) not in sys.path:
    sys.path.insert(0, str(LAMBDA_DIR))
import recommender


#Fonction que sera lancée automatiquement avant chaque test pour réinitialiser les caches
#Assure que les tests soient bien indépendants et ne soient pas affectés par les résultats des tests précédents 
@pytest.fixture(autouse=True)
def reset_caches():
    recommender._recommendations_cache = None
    recommender._popularity_cache = None


#Tests pour la fonction extract_user_id

#Teste que l'extraction de userId fonctionne correctement à partir de la racine de l'événement
def test_extract_user_id_from_root():
    event = {"userId": "tmdb_1"}
    assert recommender.extract_user_id(event) == "tmdb_1"

#Teste que l'extraction de userId fonctionne correctement à partir de la section arguments de l'événement
def test_extract_user_id_from_arguments():
    event = {"arguments": {"userId": "tmdb_2"}}
    assert recommender.extract_user_id(event) == "tmdb_2"

#Teste que la fonction retourne None si userId est absent de l'événement
def test_extract_user_id_missing():
    event = {"arguments": {}}
    assert recommender.extract_user_id(event) is None


#Tests pour la fonction get_recommendations_for_user

#Teste que les recommandations retournées n'incluent pas les films déjà notés par l'utilisateur
def test_get_recommendations_for_user_excludes_already_rated():
    user_ratings = [
        {"movieId": "1", "rating": 9},
    ]
    already_rated = {"1", "2"}
    recommendations_map = {
        "1": ["2", "3", "4"]
    }
    popularity_map = {
        "2": 0.9,
        "3": 0.4,
        "4": 0.3
    }

    recs = recommender.get_recommendations_for_user(
        user_ratings,
        already_rated,
        recommendations_map,
        popularity_map,
        limit=10
    )

    assert "2" not in recs
    assert "3" in recs or "4" in recs

#Teste que les recommandations retournées prènnent en compte les notes positives de l'utilisateur
def test_get_recommendations_for_user_positive_signal():
    user_ratings = [
        {"movieId": "10", "rating": 9.5},
    ]
    already_rated = {"10"}
    recommendations_map = {
        "10": ["20", "21", "22"]
    }
    popularity_map = {
        "20": 0.1,
        "21": 0.1,
        "22": 0.1
    }

    recs = recommender.get_recommendations_for_user(
        user_ratings,
        already_rated,
        recommendations_map,
        popularity_map,
        limit=3
    )

    assert recs == ["20", "21", "22"]

#Teste que les recommandations retournées prènnent en compte les notes négatives de l'utilisateur
def test_get_recommendations_for_user_negative_signal():
    user_ratings = [
        {"movieId": "10", "rating": 2.0},
    ]
    already_rated = {"10"}
    recommendations_map = {
        "10": ["20", "21", "22"]
    }
    popularity_map = {
        "20": 0.0,
        "21": 0.0,
        "22": 0.0
    }

    recs = recommender.get_recommendations_for_user(
        user_ratings,
        already_rated,
        recommendations_map,
        popularity_map,
        limit=3
    )

    assert recs == []

#Teste que les recommandations retournées prènnent en compte la popularité des films
def test_get_recommendations_for_user_uses_popularity():
    user_ratings = [
        {"movieId": "10", "rating": 8.0},
    ]
    already_rated = {"10"}
    recommendations_map = {
        "10": ["20", "21"]
    }
    popularity_map = {
        "20": 0.1,
        "21": 1.0
    }

    recs = recommender.get_recommendations_for_user(
        user_ratings,
        already_rated,
        recommendations_map,
        popularity_map,
        limit=2
    )

    assert len(recs) == 2


#Tests pour la fonction handler

#Teste que la fonction handler lève une erreur si userId est absent de l'événement
def test_handler_raises_when_user_id_missing():
    with pytest.raises(ValueError, match="userId not found in event"):
        recommender.handler({}, None)

#Teste que la fonction handler retourne une liste vide de recommandations si l'utilisateur n'a aucune note
def test_handler_returns_empty_when_no_ratings(monkeypatch):
    #Simule une fonction get_user_ratings qui retourne une liste vide pour l'utilisateur
    monkeypatch.setattr(recommender, "get_user_ratings", lambda user_id: [])

    event = {"userId": "tmdb_1"}
    result = recommender.handler(event, None)

    assert result["userId"] == "tmdb_1"
    assert result["recommendations"] == []

#Test complet de la fonction handler
def test_handler_returns_recommendations(monkeypatch):
    fake_user_ratings = [
        {"userId": "tmdb_1", "movieId": "10", "rating": 9.0},
        {"userId": "tmdb_1", "movieId": "11", "rating": 8.0},
    ]

    fake_recommendations = {
        "10": ["20", "21", "22"],
        "11": ["21", "23", "24"]
    }

    fake_popularity = {
        "20": 0.2,
        "21": 0.9,
        "22": 0.1,
        "23": 0.4,
        "24": 0.3
    }

    #Simule les fonctions de chargement des données pour retourner les données factices
    monkeypatch.setattr(recommender, "get_user_ratings", lambda user_id: fake_user_ratings)
    monkeypatch.setattr(recommender, "load_recommendations_from_s3", lambda: fake_recommendations)
    monkeypatch.setattr(recommender, "load_popularity_from_s3", lambda: fake_popularity)

    event = {"userId": "tmdb_1"}
    result = recommender.handler(event, None)

    assert result["userId"] == "tmdb_1"
    assert isinstance(result["recommendations"], list)
    assert len(result["recommendations"]) > 0
    assert "10" not in result["recommendations"]
    assert "11" not in result["recommendations"]

