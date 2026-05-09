import unittest

from aws_fakes import (
    FakeDynamoResource,
    FakeDynamoTable,
    load_module,
    patched_boto3,
    patched_environment,
)


class GetMovieByGenreLambdaTests(unittest.TestCase):

    def load_genre_module(self, movie_table=None):
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

    # TU-06
    def test_handler_returns_best_movie_for_genre(self):
        """
        Cas nominal : la Lambda retourne le premier film disponible
        pour le genre demandé.
        """
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

        self.assertEqual(result["movieId"], "film-1")
        self.assertEqual(result["title"], "Matrix")
        self.assertEqual(result["mainGenre"], 28)

    #TU-07
    def test_handler_excludes_already_seen_movies(self):
        """
        Les films dont le movieId est dans excludedIds ne doivent
        pas apparaître dans le résultat.
        Ici les 2 premiers films sont exclus, le 3ème doit être retourné.
        """
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

        result = module.handler({"genreId": 28, "excludedIds": ["film-1", "film-2"]}, None)

        self.assertEqual(result["movieId"], "film-3")

    #TU-08
    def test_handler_returns_none_when_all_movies_excluded(self):
        """
        Si tous les films du genre sont dans excludedIds,
        retourner movieId=None avec un message explicatif.
        """
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

        result = module.handler({"genreId": 28, "excludedIds": ["film-1"]}, None)

        self.assertIsNone(result["movieId"])
        self.assertIn("message", result)

    # TU-09
    def test_handler_rejects_missing_genre_id(self):
        """
        Si genreId est absent de l'event, une ValueError doit être levée.
        """
        module, _ = self.load_genre_module()

        with self.assertRaisesRegex(ValueError, "genreId est requis"):
            module.handler({"excludedIds": []}, None)


if __name__ == "__main__":
    unittest.main()