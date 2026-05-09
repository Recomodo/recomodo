import unittest

from aws_fakes import (
    FakeDynamoResource,
    FakeDynamoTable,
    FakeS3Client,
    load_module,
    patched_boto3,
    patched_environment,
)


class RecommenderLambdaTests(unittest.TestCase):
    def load_recommender(self, ratings_items=None, recommendations=None):
        env = {
            "RATINGS_TABLE_NAME": "ratings-table",
            "RATINGS_USER_ID_INDEX": "byUserId",
            "DATA_BUCKET_NAME": "data-bucket",
            "MOVIES_RECOMMENDATIONS_KEY": "recomodo/recommendations.json",
        }
        ratings_table = FakeDynamoTable(
            {
                "byUserId": [
                    {"Items": ratings_items or []},
                ]
            }
        )
        fake_dynamodb = FakeDynamoResource({"ratings-table": ratings_table})
        fake_s3 = FakeS3Client(
            {
                ("data-bucket", "recomodo/recommendations.json"): recommendations
                or {}
            }
        )

        with patched_environment(env), patched_boto3(fake_dynamodb, fake_s3):
            module = load_module(
                "recommender_under_test",
                "amplify/functions/recommender/recommender.py",
            )

        return module, ratings_table, fake_s3

    def test_extract_user_id_accepts_root_or_arguments(self):
        module, _, _ = self.load_recommender()

        self.assertEqual(module.extract_user_id({"userId": "user-1"}), "user-1")
        self.assertEqual(
            module.extract_user_id({"arguments": {"userId": "user-2"}}),
            "user-2",
        )
        self.assertIsNone(module.extract_user_id({"arguments": {}}))

    def test_top_rated_movies_sorts_by_rating_and_ignores_missing_movie_ids(self):
        module, _, _ = self.load_recommender()

        result = module.top_rated_movies(
            [
                {"movieId": "low", "rating": "2"},
                {"movieId": None, "rating": "10"},
                {"movieId": "high", "rating": "9.5"},
                {"movieId": 42, "rating": 7},
            ],
            limit=2,
        )

        self.assertEqual(result, ["high", "42"])

    def test_get_recommendations_excludes_rated_movies_and_duplicates(self):
        module, _, _ = self.load_recommender()

        result = module.get_recommendations_for_user(
            top_movies_id=["m1", "m2"],
            already_rated_movies={"m1", "already-rated"},
            recommendations_map={
                "m1": ["already-rated", "rec-1", "rec-2"],
                "m2": ["rec-2", "rec-3"],
            },
        )

        self.assertEqual(result, ["rec-1", "rec-2", "rec-3"])

    def test_load_recommendations_uses_s3_cache_after_first_read(self):
        module, _, fake_s3 = self.load_recommender(
            recommendations={"m1": ["rec-1"]}
        )

        first = module.load_recommendations_from_s3()
        second = module.load_recommendations_from_s3()

        self.assertEqual(first, {"m1": ["rec-1"]})
        self.assertIs(first, second)
        self.assertEqual(len(fake_s3.calls), 1)

    def test_handler_returns_empty_recommendations_when_user_has_no_ratings(self):
        module, _, fake_s3 = self.load_recommender(ratings_items=[])

        result = module.handler({"arguments": {"userId": "user-1"}}, None)

        self.assertEqual(result, {"userId": "user-1", "recommendations": []})
        self.assertEqual(fake_s3.calls, [])

    def test_handler_recommends_from_top_rated_movies_and_filters_seen_movies(self):
        module, _, _ = self.load_recommender(
            ratings_items=[
                {"movieId": "liked", "rating": "9"},
                {"movieId": "also-liked", "rating": "8"},
                {"movieId": "already-seen", "rating": "1"},
            ],
            recommendations={
                "liked": ["already-seen", "rec-1", "rec-2"],
                "also-liked": ["rec-2", "rec-3"],
            },
        )

        result = module.handler({"arguments": {"userId": "user-1"}}, None)

        self.assertEqual(
            result,
            {
                "userId": "user-1",
                "recommendations": ["rec-1", "rec-2", "rec-3"],
            },
        )

    def test_handler_rejects_event_without_user_id(self):
        module, _, _ = self.load_recommender()

        with self.assertRaisesRegex(ValueError, "userId not found"):
            module.handler({"arguments": {}}, None)


if __name__ == "__main__":
    unittest.main()
