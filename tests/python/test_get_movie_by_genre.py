import unittest

from aws_fakes import (
    FakeDynamoResource, # Simule la ressource DynamoDB d'AWS
    FakeDynamoTable, # Simule une table DynamoDB (sans toucher à AWS)
    load_module, # Charge le fichier .py de la Lambda à tester
    patched_boto3, # Remplace boto3 (la vraie librairie AWS) par une version fake
    patched_environment, # Simule les variables d'environnement (noms des tables etc.)
)


class GetMovieByGenreLambdaTests(unittest.TestCase):

    def load_genre_module(self, movie_table=None):
        """Prépare l'environnement de test pour la Lambda getMovieByGenre."""
        env = {
            "MOVIE_TABLE_NAME": "movie-table",
            "MOVIE_MAIN_GENRE_INDEX": "byMainGenre",
        }
        fake_dynamodb = FakeDynamoResource(
            {"movie-table": movie_table or FakeDynamoTable()}
        )

        with patched_environment(env), patched_boto3(fake_dynamodb=fake_dynamodb):
            module = load_module(
                "get_movie_by_genre_under_test",
                "amplify/functions/getMovieByGenre/getMovieByGenre.py",
            )

        return module, fake_dynamodb


    def test_handler_returns_best_movie_for_genre(self):
        """
        Cas nominal : la Lambda retourne le premier film disponible
        pour le genre demandé.
        """
        #on crée une table Dynamo factice avec un film 
        movie_table = FakeDynamoTable(
            {
                "byMainGenre": [
                    {
                        "Items": [
                            {
                                "movieId": "film-1",
                                "title": "Matrix",
                                "mainGenre": 28,
                                "voteAverage": "8.5",
                                "genres": [28],
                                "posterPath": "/matrix.jpg",
                                "overview": "Un film de SF.",
                            }
                        ]
                    }
                ]
            }
        )
        module, _ = self.load_genre_module(movie_table)

        result = module.handler({"genreId": 28, "excludedIds": []}, None)
        #le film retourné doit être "film-1" / "Matrix" / genre 28
        self.assertEqual(result["movieId"], "film-1")
        self.assertEqual(result["title"], "Matrix")
        self.assertEqual(result["mainGenre"], 28)

    
    def test_handler_excludes_already_seen_movies(self):
        """
        Les films dont le movieId est dans excludedIds ne doivent
        pas apparaître dans le résultat.
        Ici les 2 premiers films sont exclus, le 3ème doit être retourné.
        """

        #on crée une table Dynamo factice avec 3 films du genre 28
        movie_table = FakeDynamoTable(
            {
                "byMainGenre": [
                    {
                        "Items": [
                            {"movieId": "film-1", "title": "Film A", "mainGenre": 28, "voteAverage": "9.0", "genres": [28], "posterPath": "/a.jpg", "overview": ""},
                            {"movieId": "film-2", "title": "Film B", "mainGenre": 28, "voteAverage": "8.0", "genres": [28], "posterPath": "/b.jpg", "overview": ""},
                            {"movieId": "film-3", "title": "Film C", "mainGenre": 28, "voteAverage": "7.0", "genres": [28], "posterPath": "/c.jpg", "overview": ""},
                        ]
                    }
                ]
            }
        )
        module, _ = self.load_genre_module(movie_table)
        #on exclut les 2 premiers films dans l'event
        result = module.handler({"genreId": 28, "excludedIds": ["film-1", "film-2"]}, None)
        # La Lambda doit retourner film-3, le seul non exclu
        self.assertEqual(result["movieId"], "film-3")

    
    def test_handler_returns_none_when_all_movies_excluded(self):
        """
        Si tous les films du genre sont dans excludedIds,
        retourner movieId=None avec un message explicatif.
        """
        #une table avec un seul film
        movie_table = FakeDynamoTable(
            {
                "byMainGenre": [
                    {
                        "Items": [
                            {"movieId": "film-1", "title": "Film A", "mainGenre": 28, "voteAverage": "8.0", "genres": [28], "posterPath": "/a.jpg", "overview": ""},
                        ]
                    }
                ]
            }
        )
        module, _ = self.load_genre_module(movie_table)
        #on exclut ce film dans l'event
        result = module.handler({"genreId": 28, "excludedIds": ["film-1"]}, None)

        self.assertIsNone(result["movieId"])
        self.assertIn("message", result)

    
    def test_handler_rejects_missing_genre_id(self):
        """
        Si genreId est absent de l'event, une ValueError doit être levée.
        """

        # table vide 
        module, _ = self.load_genre_module()

        with self.assertRaisesRegex(ValueError, "genreId est requis"):
            module.handler({"excludedIds": []}, None)


if __name__ == "__main__":
    unittest.main()