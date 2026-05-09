# Prompt utilisé avec L'IA :
# "En utilisant aws_fakes.py, écris un ensemble de tests unitaires
# pour la Lambda updateMovieRating.py en couvrant les cas suivants :
# extraire les arguments depuis la racine ou depuis event['arguments'],
# récupérer toutes les pages DynamoDB via query_all_items, rejeter
# les arguments manquants, mettre à jour une note existante et
# recalculer voteAverage, créer une nouvelle note quand l'utilisateur
# n'a jamais noté le film, et retourner une erreur quand le film
# est introuvable."

import unittest
import unittest.mock # Permet d'utiliser unittest.mock.ANY pour ignorer des valeurs imprévisibles (ex: timestamps)
from decimal import Decimal

from aws_fakes import (
    FakeDynamoResource,
    FakeDynamoTable,
    load_module,
    patched_boto3,
    patched_environment,
)


class UpdateMovieRatingLambdaTests(unittest.TestCase):
    def load_update_module(self, rating_table=None, movie_table=None):
        """Prépare l'environnement de test pour la Lambda updateMovieRating."""

        #variables d'environnement que la lambda lit au démarrage
        env = {
            "RATING_TABLE_NAME": "rating-table",
            "MOVIE_TABLE_NAME": "movie-table",
            "RATING_USER_ID_INDEX": "byUserId",
            "RATING_MOVIE_ID_INDEX": "byMovieId",
            "MOVIE_MOVIE_ID_INDEX": "byMovieId",
        }
        fake_dynamodb = FakeDynamoResource(
            {
                "rating-table": rating_table or FakeDynamoTable(),
                "movie-table": movie_table or FakeDynamoTable(),
            }
        )

        with patched_environment(env), patched_boto3(fake_dynamodb=fake_dynamodb):
            module = load_module(
                "update_movie_rating_under_test",
                "amplify/functions/updateMovieRating/updateMovieRating.py",
            )

        return module, fake_dynamodb

    def test_extract_arguments_accepts_appsync_arguments_or_root_payload(self):
        """" Vérifie que extract_arguments() fonctionne dans les deux cas :
             - arguments à la racine de l'event (appel direct)
             - arguments dans event["arguments"] (format AppSync)"""
        module, _ = self.load_update_module()

        # Cas AppSync : les arguments sont dans event["arguments"]
        self.assertEqual(
            module.extract_arguments({"arguments": {"userId": "user-1"}}),
            {"userId": "user-1"},
        )

        # Cas appel direct : les arguments sont à la racine de l'event
        self.assertEqual(
            module.extract_arguments({"userId": "user-2"}),
            {"userId": "user-2"},
        )

    def test_query_all_items_reads_every_paginated_page(self):
        """
        Vérifie que query_all_items() récupère toutes les pages DynamoDB en suivant LastEvaluatedKey,
        et pas seulement la première page.
        """
        module, _ = self.load_update_module()
        table = FakeDynamoTable(
            {
                "byUserId": [
                    {"Items": [{"id": "first"}]},
                    {"Items": [{"id": "second"}]},
                ]
            }
        )

        result = module.query_all_items(table, "byUserId", ("eq", "userId", "u1"))

        self.assertEqual(result, [{"id": "first"}, {"id": "second"}])
        self.assertEqual(len(table.query_calls), 2)
        self.assertIsNone(table.query_calls[0]["ExclusiveStartKey"])
        self.assertEqual(table.query_calls[1]["ExclusiveStartKey"], {"page": 1})

    def test_handler_rejects_missing_required_arguments(self):
        """"Vérifier que le handler lève une ValueError mentionnant
            "userId, movieId et rating" si l’un des trois paramètres
            obligatoires est absent."""
        module, _ = self.load_update_module()

        with self.assertRaisesRegex(ValueError, "userId, movieId et rating"):
            module.handler({"arguments": {"userId": "user-1", "movieId": "m1"}}, None)

    def test_handler_updates_existing_rating_and_recomputes_movie_average(self):
        """Vérifier que si l’utilisateur a déjà une note pour ce film, le
           handler utilise update_item (pas put_item) et recalcule
           voteAverage à partir des notes existantes en base."""
        rating_table = FakeDynamoTable(
            {
                "byUserId": [
                    {
                        "Items": [
                            {
                                "id": "rating-1",
                                "userId": "user-1",
                                "movieId": "movie-1",
                                "rating": Decimal("4"),
                            }
                        ]
                    }
                ],
                "byMovieId": [
                    {
                        "Items": [
                            {"rating": Decimal("8")},
                            {"rating": Decimal("6")},
                        ]
                    }
                ],
            }
        )
        movie_table = FakeDynamoTable(
            {
                "byMovieId": [
                    {"Items": [{"id": "movie-row-1", "movieId": "movie-1"}]}
                ]
            }
        )
        module, _ = self.load_update_module(rating_table, movie_table)

        result = module.handler(
            {
                "arguments": {
                    "userId": "user-1",
                    "movieId": "movie-1",
                    "rating": 9.5,
                }
            },
            None,
        )

        self.assertEqual(
            result,
            {"success": True, "message": "Note enregistrée et film mis à jour"},
        )
        self.assertEqual(rating_table.put_items, [])
        self.assertEqual(
            rating_table.update_items[0],
            {
                "Key": {"id": "rating-1"},
                "UpdateExpression": "SET rating = :r, updatedAt = :u",
                "ExpressionAttributeValues": {":r": Decimal("9.5"), ":u": unittest.mock.ANY},
            },
        )

        movie_update = movie_table.update_items[0]
        self.assertEqual(movie_update["Key"], {"id": "movie-row-1"})
        self.assertIn("voteAverage = :avg", movie_update["UpdateExpression"])
        self.assertIn("voteCount = :cnt", movie_update["UpdateExpression"])
        self.assertIn(":avg", movie_update["ExpressionAttributeValues"])
        self.assertIn(":cnt", movie_update["ExpressionAttributeValues"])
        self.assertEqual(movie_update["ExpressionAttributeValues"][":avg"], Decimal("7.0"))
        self.assertEqual(movie_update["ExpressionAttributeValues"][":cnt"], 2)


    def test_handler_creates_new_rating_when_user_has_not_rated_movie(self):
        """Vérifier que si l’utilisateur n’a jamais noté ce film, le handler
            crée un nouvel item Rating via put_item avec tous les
            champs requis (id, owner, __typename, etc.)."""
        rating_table = FakeDynamoTable(
            {
                "byUserId": [{"Items": []}],
                "byMovieId": [
                    {
                        "Items": [
                            {"rating": Decimal("8")},
                            {"rating": Decimal("10")},
                        ]
                    }
                ],
            }
        )
        movie_table = FakeDynamoTable(
            {
                "byMovieId": [
                    {"Items": [{"id": "movie-row-1", "movieId": "movie-1"}]}
                ]
            }
        )
        module, _ = self.load_update_module(rating_table, movie_table)

        result = module.handler(
            {"userId": "user-1", "movieId": "movie-1", "rating": 9},
            None,
        )

        self.assertTrue(result["success"])
        self.assertEqual(len(rating_table.put_items), 1)
        created = rating_table.put_items[0]
        self.assertEqual(created["userId"], "user-1")
        self.assertEqual(created["movieId"], "movie-1")
        self.assertEqual(created["rating"], Decimal("9"))
        self.assertEqual(created["owner"], "user-1")
        self.assertEqual(created["__typename"], "Rating")
        self.assertTrue(created["id"])
        self.assertEqual(movie_table.update_items[0]["Key"], {"id": "movie-row-1"})

    def test_handler_reports_missing_movie_after_saving_rating(self):
        """Vérifier que si le film est introuvable en table Movie,
           le handler retourne { success: False, message: "Film
           <movieId> introuvable" } sans créer de Rating parasite"""
        rating_table = FakeDynamoTable(
            {
                "byUserId": [{"Items": []}],
                "byMovieId": [{"Items": [{"rating": Decimal("7")}]}],
            }
        )
        movie_table = FakeDynamoTable({"byMovieId": [{"Items": []}]})
        module, _ = self.load_update_module(rating_table, movie_table)

        result = module.handler(
            {"arguments": {"userId": "user-1", "movieId": "missing", "rating": 7}},
            None,
        )

        self.assertEqual(
            result,
            {"success": False, "message": "Film missing introuvable"},
        )
        self.assertEqual(len(rating_table.put_items), 0)


if __name__ == "__main__":
    unittest.main()
