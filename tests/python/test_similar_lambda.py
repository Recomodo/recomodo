import unittest

from aws_fakes import FakeS3Client, load_module, patched_boto3, patched_environment


class SimilarLambdaTests(unittest.TestCase):
    def load_similar(self, recommendations=None):
        env = {
            "DATA_BUCKET_NAME": "data-bucket",
            "MOVIES_RECOMMENDATIONS_KEY": "recomodo/recommendations.json",
        }
        fake_s3 = FakeS3Client(
            {
                ("data-bucket", "recomodo/recommendations.json"): recommendations
                or {}
            }
        )

        with patched_environment(env), patched_boto3(fake_s3=fake_s3):
            module = load_module(
                "similar_under_test",
                "amplify/functions/similar/similar.py",
            )

        return module, fake_s3

    def test_extract_movie_id_accepts_root_or_arguments(self):
        module, _ = self.load_similar()

        self.assertEqual(module.extract_movie_id({"movieId": "movie-1"}), "movie-1")
        self.assertEqual(
            module.extract_movie_id({"arguments": {"movieId": "movie-2"}}),
            "movie-2",
        )
        self.assertIsNone(module.extract_movie_id({"arguments": {}}))

    def test_handler_returns_similar_movies_for_known_movie(self):
        module, _ = self.load_similar({"movie-1": ["movie-2", "movie-3"]})

        result = module.handler({"arguments": {"movieId": "movie-1"}}, None)

        self.assertEqual(
            result,
            {"movieId": "movie-1", "similar": ["movie-2", "movie-3"]},
        )

    def test_handler_returns_empty_list_for_unknown_movie(self):
        module, _ = self.load_similar({"movie-1": ["movie-2"]})

        result = module.handler({"arguments": {"movieId": "missing"}}, None)

        self.assertEqual(result, {"movieId": "missing", "similar": []})

    def test_handler_rejects_event_without_movie_id(self):
        module, _ = self.load_similar()

        with self.assertRaisesRegex(ValueError, "movieId not found"):
            module.handler({"arguments": {}}, None)

    def test_load_recommendations_uses_s3_cache_after_first_read(self):
        module, fake_s3 = self.load_similar({"movie-1": ["movie-2"]})

        first = module.load_recommendations_from_s3()
        second = module.load_recommendations_from_s3()

        self.assertEqual(first, {"movie-1": ["movie-2"]})
        self.assertIs(first, second)
        self.assertEqual(len(fake_s3.calls), 1)


if __name__ == "__main__":
    unittest.main()
