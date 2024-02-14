import datetime
import json

import pyotp
import requests


class KeycloakToken:
    """Gives keycloak token details"""

    def __init__(self):
        self.generation_date = self.expiration_date = self.token = None


def get_keycloak_response(json_data: json) -> dict:
    """Gets response from sending a POST request to the given keycloak address."""
    totp = ""
    if "totp_code" in json_data:
        totp = (
            pyotp.TOTP(json_data["totp_code"].replace(" ", "")).now()
            if json_data["totp_code"] != ""
            else totp
        )
    data = {
        "client_id": json_data["client_id"],
        "username": json_data["username"],
        "password": json_data["password"],
        "grant_type": "password",
        "client_secret": json_data["client_secret"],
        "totp": totp,
    }
    try:
        r = requests.post(
            json_data["keycloak_address"],
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        r.raise_for_status()
    except Exception:
        raise Exception(
            f"Keycloak token creation failed. Response from the server was: {r.json()}"
        )
    return r.json()


def generate_headers(keycloak: KeycloakToken, json_data: json) -> dict:
    """Generates headers."""
    try:
        if not keycloak.generation_date or (
            keycloak.expiration_date
            < datetime.datetime.now() + datetime.timedelta(seconds=40)
        ):
            keycloak_response = get_keycloak_response(json_data)
            keycloak.token = keycloak_response["access_token"]
            keycloak.generation_date = datetime.datetime.now()
            keycloak.expiration_date = keycloak.generation_date + datetime.timedelta(
                seconds=keycloak_response["expires_in"]
            )
            print("Token has been generated, proceeding with the order")
        else:
            print("Token in still valid, proceeding with the order")
    except Exception as e:
        raise Exception(f"Validation failed. Reason: {e}")

    if "host" in json_data:
        headers = {
            "Authorization": f"access_token {keycloak.token}",
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Host": json_data["host"],
        }
    else:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {keycloak.token}",
        }

    return headers
