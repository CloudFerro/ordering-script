import json
import requests
import datetime
import os
import urllib3
import pyotp

from typing import Any
from time import sleep

ORDERING_KEYCLOAK_GENERATION_DATE = ORDERING_KEYCLOAK_EXPIRATION_DATE = ORDERING_KEYCLOAK_TOKEN = \
    CATALOGUE_KEYCLOAK_GENERATION_DATE = CATALOGUE_KEYCLOAK_EXPIRATION_DATE = CATALOGUE_KEYCLOAK_TOKEN = ""
RETRY_COUNT = 0
PWD = os.path.dirname(os.path.realpath(__file__))

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_keycloak_response(file: str) -> dict:
    """Gets response from sending a POST request to the given keycloak address."""
    variables = get_json_from_file(file)
    totp = ""
    if "totp_code" in variables:
        totp = pyotp.TOTP(variables["totp_code"].replace(" ", "")).now() if variables["totp_code"] != "" else totp
    data = {
        "client_id": variables["client_id"],
        "username": variables["username"],
        "password": variables["password"],
        "grant_type": "password",
        "client_secret": variables["client_secret"],
        "totp": totp
    }
    try:
        r = requests.post(
            variables["keycloak_address"],
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        r.raise_for_status()
    except Exception:
        raise Exception(f"Keycloak token creation failed. Response from the server was: {r.json()}")
    return r.json()


def cls() -> None:
    """Clears console."""
    os.system('cls' if os.name == 'nt' else 'clear')


def generate_ordering_headers() -> dict:
    """Generates ordering headers."""
    global ORDERING_KEYCLOAK_GENERATION_DATE, ORDERING_KEYCLOAK_EXPIRATION_DATE, ORDERING_KEYCLOAK_TOKEN
    try:
        if not ORDERING_KEYCLOAK_GENERATION_DATE or (
                ORDERING_KEYCLOAK_EXPIRATION_DATE < datetime.datetime.now() + datetime.timedelta(seconds=40)):
            keycloak_response = get_keycloak_response("keycloak_ordering.json")
            ORDERING_KEYCLOAK_TOKEN = keycloak_response["access_token"]
            ORDERING_KEYCLOAK_GENERATION_DATE = datetime.datetime.now()
            ORDERING_KEYCLOAK_EXPIRATION_DATE = ORDERING_KEYCLOAK_GENERATION_DATE + datetime.timedelta(
                seconds=keycloak_response["expires_in"])
            print("Token has been generated, proceeding with the order")
        else:
            print("Token in still valid, proceeding with the order")
    except Exception as e:
        raise Exception(f"Validation failed. Reason: {e}")

    variables = get_json_from_file("keycloak_ordering.json")
    headers = {
        "Authorization": f"access_token {ORDERING_KEYCLOAK_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Host": variables["host"]
    }

    return headers


def generate_catalogue_headers() -> dict:
    """Generates catalogue headers."""
    global CATALOGUE_KEYCLOAK_GENERATION_DATE, CATALOGUE_KEYCLOAK_EXPIRATION_DATE, CATALOGUE_KEYCLOAK_TOKEN
    try:
        if not CATALOGUE_KEYCLOAK_GENERATION_DATE or (
                CATALOGUE_KEYCLOAK_EXPIRATION_DATE < datetime.datetime.now() + datetime.timedelta(seconds=120)):
            keycloak_response = get_keycloak_response("keycloak_catalogue.json")
            CATALOGUE_KEYCLOAK_TOKEN = keycloak_response["access_token"]
            CATALOGUE_KEYCLOAK_GENERATION_DATE = datetime.datetime.now()
            CATALOGUE_KEYCLOAK_EXPIRATION_DATE = CATALOGUE_KEYCLOAK_GENERATION_DATE + datetime.timedelta(
                seconds=keycloak_response["expires_in"])
            print("Token has been generated, proceeding with the order")
        else:
            print("Token in still valid, proceeding with the order")
    except Exception as e:
        raise Exception(f"Validation failed. Reason: {e}")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CATALOGUE_KEYCLOAK_TOKEN}",
    }

    return headers


def get_json_from_file(file: str) -> json:
    """Gets json from given file."""
    with open(f"{PWD}/json/{file}") as f:
        output = json.load(f)
    return output


def generate_order_body_from_query(order_body: json, identifiers: list) -> json:
    """Generates order body and prepares IdentifierList parameter."""
    order_body["IdentifierList"] = identifiers
    print("Order body has been generated")
    return order_body


def send_post_request_to_batch_order_and_validate_response(order_body: dict) -> Any:
    """Creates new BatchOrder."""
    global RETRY_COUNT
    print("Posting order")
    variables = get_json_from_file("keycloak_ordering.json")
    response = requests.post(f"https://{variables['host']}/odata/v1/BatchOrder/OData.CSC.Order", json=order_body,
                             headers=generate_ordering_headers(),
                             verify=False)
    match response.status_code:
        case 201:
            print(
                f"Order has been created successfully. Received status code: {response.status_code}. Received "
                f"response:\n{response.json()}.\nOrder id: {response.json()['value']['Id']}")
        case _:
            if response.status_code < 500:
                print(
                    f"Order hasn't been created successfully. Received response:\n{response.json()}\nReceived status "
                    f"code {response.status_code}. Sending another request with a body: {order_body}")
            else:
                print(
                    f"Order hasn't been created successfully. Received status code {response.status_code}. Sending "
                    f"another request with a body: {order_body}")
            if RETRY_COUNT % 4 != 0 or RETRY_COUNT == 0:
                RETRY_COUNT += 1
                sleep(2)
                send_post_request_to_batch_order_and_validate_response(order_body)
    RETRY_COUNT = 0
    return response


def create_batch_order_with_body() -> None:
    """Option 1 - Creates new BatchOrder with a given body."""
    order_body = get_json_from_file("order_body.json")
    send_post_request_to_batch_order_and_validate_response(order_body)


def wait_for_order_to_be_processed(identifier: int) -> None:
    """Waits for order to be processed - not in status queued or in_progress."""
    global RETRY_COUNT
    variables = get_json_from_file("keycloak_ordering.json")
    print("Waiting for order to be processed...")
    while True:
        response = requests.get(
            f"https://{variables['host']}/odata/v1/BatchOrder({identifier})",
            headers=generate_ordering_headers(), verify=False)
        if response.status_code == 200:
            if response.json()["value"]["Status"] != "queued" and response.json()["value"]["Status"] != "in_progress":
                RETRY_COUNT = 0
                print(f"Order has been processed. Status: {response.json()['value']['Status']}")
                break
            sleep(30)
        else:
            if RETRY_COUNT % 4 != 0 or RETRY_COUNT == 0:
                RETRY_COUNT += 1
                print(f"Received status code {response.status_code}. Sending another request")
                sleep(2)
            else:
                RETRY_COUNT = 0


def get_response_from_next_link(next_link: str) -> json:
    """Gets response from sending a GET request to the given next link."""
    global RETRY_COUNT
    next_link_response = requests.get(next_link,
                                      headers=generate_catalogue_headers()) if "/stac/" in next_link else requests.get(
        next_link)
    if next_link_response.status_code != 200:
        if RETRY_COUNT % 4 != 0 or RETRY_COUNT == 0:
            RETRY_COUNT += 1
            print(f"Received status code {next_link_response.status_code}. Sending another request.")
            sleep(2)
            get_response_from_next_link(next_link)
    RETRY_COUNT = 0
    return next_link_response.json()


def create_batch_order_with_query(hours: int | None = None) -> None:
    """Option 2 - Creates new BatchOrder with a given queryURL."""
    global RETRY_COUNT
    if hours:
        modify_query_by_given_hour_mark(hours)

    print("Getting response from the given queryURL")
    variables = get_json_from_file("query.json")
    response = requests.get(f"{variables['queryURL']}&$count=true") if "/stac/" not in variables[
        'queryURL'] else requests.get(variables['queryURL'], headers=generate_catalogue_headers())
    identifiers = []

    if response.status_code == 200:
        if variables["new_orders"]:
            create_batch_order_with_query_new_orders(variables, response.json(), identifiers)
        else:
            create_batch_order_with_query_no_new_orders(variables, response.json(), identifiers)
    else:
        if RETRY_COUNT % 4 != 0 or RETRY_COUNT == 0:
            RETRY_COUNT += 1
            print(f"Received status code {response.status_code}. Sending another request.")
            sleep(2)
            create_batch_order_with_query()
        RETRY_COUNT = 0


def create_batch_order_with_query_no_new_orders(variables: json, response: json, identifiers: list) -> None:
    """Option 2 - Creates new BatchOrder with a given queryURL, without waiting for order to be processed."""
    while response:
        products = response["value"] if "value" in response else response["features"]
        products_count = response["@odata.count"] if "@odata.count" in response else response["numberMatched"]
        total_items = 0
        for product in products:
            if len(identifiers) < variables["parallel_quota"]:
                identifiers.append(product["Name"]) if "Name" in product else identifiers.append(product["id"])
                total_items += 1
                print(f"Loaded {identifiers[-1]} to a list of products")
            if len(identifiers) == variables["parallel_quota"] or products_count == total_items:
                order_body = generate_order_body_from_query(get_json_from_file("order_body.json"), identifiers)
                send_post_request_to_batch_order_and_validate_response(order_body)
                break

        if "@odata.nextLink" in response and len(identifiers) < variables["parallel_quota"]:
            print(f"All products have been loaded to a list. Going to another link for more products: {response['@odata.nextLink']}")
            response = get_response_from_next_link(response["@odata.nextLink"])
        elif "links" in response and len(identifiers) < variables["parallel_quota"]:
            for link in response["links"]:
                if link["rel"] == "next":
                    print(f"All products have been loaded to a list. Going to another link for more products: {link['href']}")
                    response = get_response_from_next_link(link["href"])
        else:
            break


def create_batch_order_with_query_new_orders(variables: json, response: json, identifiers: list) -> None:
    """Option 2 - Creates new BatchOrder with a given queryURL, with waiting for order to be processed."""
    products_count = response["@odata.count"] if "@odata.count" in response else response["numberMatched"]
    total_items = 0
    while response:
        products = response["value"] if "value" in response else response["features"]
        for product in products:
            if len(identifiers) < variables["parallel_quota"]:
                identifiers.append(product["Name"]) if "Name" in product else identifiers.append(product["id"])
                total_items += 1
                print(f"Loaded {identifiers[-1]} to a list of products")
            if len(identifiers) == variables["parallel_quota"] or products_count == total_items:
                order_body = generate_order_body_from_query(get_json_from_file("order_body.json"), identifiers)
                post_response = send_post_request_to_batch_order_and_validate_response(order_body)
                if "value" in post_response.json():
                    wait_for_order_to_be_processed(post_response.json()["value"]["Id"])
                    identifiers.clear()
                else:
                    break

        if "@odata.nextLink" in response and len(identifiers) < variables["parallel_quota"]:
            print(
                f"All products have been loaded to a list. Going to another link for more products: "
                f"{response['@odata.nextLink']}")
            response = get_response_from_next_link(response["@odata.nextLink"])
        elif "links" in response and len(identifiers) < variables["parallel_quota"]:
            link_counter = 0
            for link in response["links"]:
                link_counter += 1
                if link["rel"] == "next":
                    print(
                        f"All products have been loaded to a list. Going to another link for more products: "
                        f"{link['href']}")
                    response = get_response_from_next_link(link["href"])
                elif link_counter == len(response["links"]):
                    break
        else:
            break


def add_timezone_chars_to_date(date: str) -> str:
    """Adds 'T' and 'Z' chars to the given date."""
    date = date.replace(" ", "T")
    date += "Z"
    return date


def get_date_from_query(query_url: str, sub1: str, sub2: str) -> str:
    """Extracts date from query."""
    idx1 = query_url.index(sub1)
    idx2 = query_url.index(sub2)

    res = ""
    for idx in range(idx1 + len(sub1) + 1, idx2):
        res = res + query_url[idx]

    return res


def modify_query_by_given_hour_mark(hours: int) -> None:
    """Modifies queryURL variable to take into account 'hours' variable specified by the user."""
    with open(f"{PWD}/json/query.json", "r+") as jsonFile:
        data = json.load(jsonFile)
        query_url = data["queryURL"]
        current_date = datetime.datetime.now()
        earlier_date = str(current_date - datetime.timedelta(hours=hours))
        current_date = str(current_date)
        current_date = add_timezone_chars_to_date(current_date)
        earlier_date = add_timezone_chars_to_date(earlier_date)

        if "/stac/" in query_url:
            query_url += f"&datetime={earlier_date}/{current_date}"
        else:
            res = get_date_from_query(query_url, "ContentDate/Start%20le%2", ")%20and%20(Online")
            query_url = query_url.replace(res, current_date)

            res2 = get_date_from_query(query_url, "ContentDate/Start%20ge%2", "%20and%20ContentDate")
            query_url = query_url.replace(res2, earlier_date)

        data["queryURL"] = query_url
        jsonFile.seek(0)
        json.dump(data, jsonFile)
        jsonFile.truncate()


def check_order_details(order_id: int) -> None:
    """Option 3 - Outputs json from BatchOrder(order_id)"""
    variables = get_json_from_file("keycloak_ordering.json")
    response = requests.get(f"https://{variables['host']}/odata/v1/BatchOrder({order_id})",
                            headers=generate_ordering_headers(),
                            verify=False)
    print(response.json())
