# Prompt utilisé avec l'IA :
# "Voici le code source de mes Lambdas Python (getMovieByGenre.py,
# updateMovieRating.py) et la structure de mon projet AWS Amplify.
# Génère un fichier utilitaire qui me permette d'écrire des tests
# unitaires sans connexion réelle à AWS, en simulant DynamoDB et S3,
# en fournissant un faux environnement de variables et en chargeant
# dynamiquement les modules Python à tester."

import importlib.util
import json
import os
import sys
import types
from contextlib import contextmanager
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class FakeKey:
    def __init__(self, name):
        self.name = name

    def eq(self, value):
        return ("eq", self.name, value)


class FakeBody:
    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return self.payload


class FakeS3Client:
    def __init__(self, objects=None):
        self.objects = objects or {}
        self.calls = []

    def get_object(self, Bucket, Key):
        self.calls.append({"Bucket": Bucket, "Key": Key})
        payload = self.objects[(Bucket, Key)]
        if isinstance(payload, (dict, list)):
            payload = json.dumps(payload)
        if isinstance(payload, str):
            payload = payload.encode("utf-8")
        return {"Body": FakeBody(payload)}


class FakeDynamoResource:
    def __init__(self, tables=None):
        self.tables = tables or {}
        self.requested_tables = []

    def Table(self, name):
        self.requested_tables.append(name)
        return self.tables.setdefault(name, FakeDynamoTable())


class FakeSession:
    def __init__(self, dynamodb):
        self.dynamodb = dynamodb

    def resource(self, service_name):
        if service_name != "dynamodb":
            raise AssertionError(f"Unexpected resource: {service_name}")
        return self.dynamodb


class FakeDynamoTable:
    def __init__(self, query_pages_by_index=None):
        self.query_pages_by_index = query_pages_by_index or {}
        self.query_calls = []
        self.put_items = []
        self.update_items = []

    def query(self, IndexName, KeyConditionExpression, ExclusiveStartKey=None,  ScanIndexForward=True, Limit=None):
        self.query_calls.append(
            {
                "IndexName": IndexName,
                "KeyConditionExpression": KeyConditionExpression,
                "ExclusiveStartKey": ExclusiveStartKey,
                "ScanIndexForward": ScanIndexForward,
                "Limit": Limit,
            }
        )

        pages = self.query_pages_by_index.get(IndexName, [{"Items": []}])
        page_index = 0 if ExclusiveStartKey is None else ExclusiveStartKey["page"]
        page = dict(pages[page_index])

        if page_index + 1 < len(pages):
            page["LastEvaluatedKey"] = {"page": page_index + 1}

        return page

    def put_item(self, Item):
        self.put_items.append(Item)

    def update_item(self, **kwargs):
        self.update_items.append(kwargs)


@contextmanager
def patched_environment(values):
    old_values = {key: os.environ.get(key) for key in values}
    os.environ.update(values)
    try:
        yield
    finally:
        for key, old_value in old_values.items():
            if old_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value


@contextmanager
def patched_boto3(fake_dynamodb=None, fake_s3=None):
    fake_dynamodb = fake_dynamodb or FakeDynamoResource()
    fake_s3 = fake_s3 or FakeS3Client()

    boto3_module = types.ModuleType("boto3")
    boto3_module.resource = lambda service_name: fake_dynamodb
    boto3_module.client = lambda service_name: fake_s3
    boto3_module.Session = lambda profile_name=None: FakeSession(fake_dynamodb)

    dynamodb_module = types.ModuleType("boto3.dynamodb")
    conditions_module = types.ModuleType("boto3.dynamodb.conditions")
    conditions_module.Key = FakeKey
    conditions_module.Attr = FakeKey

    module_names = {
        "boto3": boto3_module,
        "boto3.dynamodb": dynamodb_module,
        "boto3.dynamodb.conditions": conditions_module,
    }
    sentinel = object()
    old_modules = {name: sys.modules.get(name, sentinel) for name in module_names}
    sys.modules.update(module_names)

    try:
        yield
    finally:
        for name, old_module in old_modules.items():
            if old_module is sentinel:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old_module


def load_module(module_name, relative_path):
    path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
