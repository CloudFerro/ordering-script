import json
import os
from typing import Final

PWD: Final = os.path.dirname(os.path.realpath(__file__))


def get_json_from_file(file: str) -> json:
    """Gets json from given file."""
    with open(f"{PWD}/jsons/{file}") as f:
        output = json.load(f)
    return output


def get_keycloak_ordering() -> json:
    """Gets keycloak_ordering.json"""
    return get_json_from_file("keycloak_ordering.json")


def get_keycloak_catalogue() -> json:
    """Gets keycloak_catalogue.json"""
    return get_json_from_file("keycloak_catalogue.json")


def get_order_body() -> json:
    """Gets order_body.json"""
    return get_json_from_file("order_body.json")


def get_order_details() -> json:
    """Gets order_details.json"""
    return get_json_from_file("order_details.json")


def get_query_details() -> json:
    """Gets query_details.json"""
    return get_json_from_file("query_details.json")
