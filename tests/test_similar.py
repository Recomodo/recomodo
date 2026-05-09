import os
import pytest
import sys
from pathlib import Path

#Variables d'environnement minimales pour permettre l'import de recommender.py
os.environ.setdefault("AWS_DEFAULT_REGION", "eu-west-3")
os.environ.setdefault("DATA_BUCKET_NAME", "dummy-bucket")
os.environ.setdefault("MOVIES_RECOMMENDATIONS_KEY", "dummy-key")

#Chemin vers le dossier contenant similar.py
LAMBDA_DIR = Path("amplify/functions/similar").resolve()
if str(LAMBDA_DIR) not in sys.path:
    sys.path.insert(0, str(LAMBDA_DIR))
import similar

#Fonction que sera lancée automatiquement avant chaque test pour réinitialiser le cache
#Assure que les tests soient bien indépendants et ne soient pas affectés par les résultats des tests précédents 
@pytest.fixture(autouse=True)
def reset_caches():
    similar._similar_cache = None

#Tests pour la fonction extract_movie_id

#Teste que l'extraction de movieId fonctionne correctement à partir de la racine de l'événement
def test_extract_movie_id_from_root():
    event = {"movieId": "1"}
    assert similar.extract_movie_id(event) == "1"

#Teste que l'extraction de movieId fonctionne correctement à partir de la section arguments de l'événement
def test_extract_movie_id_from_arguments():
    event = {"arguments": {"movieId": "2"}}
    assert similar.extract_movie_id(event) == "2"

#Teste que la fonction retourne None si movieId est absent de l'événement
def test_extract_movie_id_missing():
    event = {"arguments": {}}
    assert similar.extract_movie_id(event) is None

#Tests pour la fonction handler

#Teste que la fonction handler lève une erreur si userId est absent de l'événement
def test_handler_raises_when_user_id_missing():
    with pytest.raises(ValueError, match="movieId not found in event"):
        similar.handler({}, None)

#Teste que la fonction handler retourne une liste vide de films similaires si le movieId n'est pas trouvé dans les recommandations pré-calculées
def test_handler_returns_empty_when_no_similar(monkeypatch):
    event = {"movieId": "1"} 
    
    fake_similar = {
        "10": ["20", "21", "22"],
        "11": ["21", "23", "24"]
    }

    #Simule les fonctions de chargement des données pour retourner les données factices
    monkeypatch.setattr(similar, "load_recommendations_from_s3", lambda: fake_similar)

    result = similar.handler(event, None)

    assert result == {
        "movieId": "1",
        "similar": []
    }

def test_handler_returns_similar(monkeypatch):
    event = {"movieId": "10"} 
    
    fake_similar = {
        "10": ["20", "21", "22"],
        "11": ["21", "23", "24"]
    }

    monkeypatch.setattr(similar, "load_recommendations_from_s3", lambda: fake_similar)

    result = similar.handler(event, None)

    assert result == {
        "movieId": "10",
        "similar": ["20", "21", "22"]
    }