import json
import urllib.parse
import requests
import datetime
import os
import urllib3

from typing import Final
from time import sleep
from retry import retry
from auth import KeycloakToken, generate_headers
from json_getter import PWD, get_keycloak_ordering, get_keycloak_catalogue, get_order_details, get_query_details, \
    get_order_body

KEYCLOAK_ORDERING_JSON: Final = get_keycloak_ordering()
KEYCLOAK_CATALOGUE_JSON: Final = get_keycloak_catalogue()
ORDER_BODY_JSON: Final = get_order_body()
ORDER_DETAILS_JSON: Final = get_order_details()
QUERY_DETAILS_JSON: Final = get_query_details()

ordering_keycloak = KeycloakToken()
catalogue_keycloak = KeycloakToken()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def cls() -> None:
    """Clears console."""
    os.system('cls' if os.name == 'nt' else 'clear')


def generate_order_body_from_query(order_body: json, identifiers: list) -> json:
    """Generates order body and prepares IdentifierList parameter."""
    order_body["IdentifierList"] = identifiers
    print("Order body has been generated")
    return order_body


@retry(tries=5, delay=5)
def send_post_request_to_batch_order_and_validate_response(order_body: dict) -> requests.Response:
    """Creates new BatchOrder."""
    print("Posting order")
    response = requests.post(f"https://{KEYCLOAK_ORDERING_JSON['host']}/odata/v1/BatchOrder/OData.CSC.Order",
                             json=order_body,
                             headers=generate_headers(ordering_keycloak, KEYCLOAK_ORDERING_JSON),
                             verify=False)
    assert response.status_code == 201, print(
        f"Order hasn't been created successfully. Received response: \n{response.json()}\nWrong status code - "
        f"{response.status_code}, expected 201. Sending "
        f"another request with: {order_body}") if response.status_code < 500 else print(
        f"Order hasn't been created successfully. Wrong status code - {response.status_code}, expected 201. Sending "
        f"another request with: {order_body}")
    print(
        f"Order has been created successfully. Received status code: {response.status_code}. Received "
        f"response:\n{response.json()}.\nOrder id: {response.json()['value']['Id']}")
    return response


def create_batch_order_with_body() -> None:
    """Option 1 - Creates new BatchOrder with a given body."""
    identifiers = []
    products_ordered = 0
    products = ORDER_BODY_JSON["IdentifierList"]
    for product in products:
        if len(identifiers) < ORDER_DETAILS_JSON["parallel_quota"]:
            identifiers.append(product)
            products_ordered += 1
            print(f"Loaded {identifiers[-1]} to a list of products")
        if len(identifiers) == ORDER_DETAILS_JSON["parallel_quota"] or len(products) == products_ordered:
            order_body = generate_order_body_from_query(ORDER_BODY_JSON, identifiers)
            response = send_post_request_to_batch_order_and_validate_response(order_body)
            if "value" in response.json():
                wait_for_order_to_be_processed(response.json()["value"]["Id"])
                identifiers.clear()
                if not ORDER_DETAILS_JSON["new_orders"]:
                    break
            else:
                break


@retry(tries=5, delay=5)
def wait_for_order_to_be_processed(identifier: int) -> None:
    """Waits for order to be processed - not in status queued or in_progress."""
    print("Waiting for order to be processed...")
    while True:
        response = requests.get(
            f"https://{KEYCLOAK_ORDERING_JSON['host']}/odata/v1/BatchOrder({identifier})",
            headers=generate_headers(ordering_keycloak, KEYCLOAK_ORDERING_JSON), verify=False)
        assert response.status_code == 200, print(
            f"Received status code {response.status_code}. Sending another request")
        if response.json()["value"]["Status"] != "queued" and response.json()["value"]["Status"] != "in_progress":
            print(f"Order has been processed. Status: {response.json()['value']['Status']}")
            break
        sleep(30)


@retry(tries=5, delay=5)
def get_response_from_next_link(next_link: str) -> dict:
    """Gets response from sending a GET request to the given next link."""
    response = requests.get(next_link, headers=generate_headers(catalogue_keycloak,
                                                                KEYCLOAK_CATALOGUE_JSON)) if "/stac/" in next_link \
        else requests.get(
        next_link)
    assert response.status_code == 200, print(f"Received status code {response.status_code}. Sending another request.")
    return response.json()


@retry(tries=5, delay=5)
def create_batch_order_with_query(hours: int | None = None) -> None:
    """Option 2 - Creates new BatchOrder with a given query_url."""
    if hours:
        modify_query_by_given_hour_mark(hours)

    print("Getting response from the given query_url")
    response = requests.get(f"{QUERY_DETAILS_JSON['query_url']}&$count=true") if "/stac/" not in QUERY_DETAILS_JSON[
        'query_url'] else requests.get(QUERY_DETAILS_JSON['query_url'],
                                       headers=generate_headers(catalogue_keycloak, KEYCLOAK_CATALOGUE_JSON))
    identifiers = []

    assert response.status_code == 200, print(f"Received status code {response.status_code}. Sending another request.")

    if QUERY_DETAILS_JSON["new_orders"]:
        create_batch_order_with_query_new_orders(QUERY_DETAILS_JSON, response.json(), identifiers)
    else:
        create_batch_order_with_query_no_new_orders(QUERY_DETAILS_JSON, response.json(), identifiers)


def create_batch_order_with_query_no_new_orders(variables: json, response: json, identifiers: list) -> None:
    """Option 2 - Creates new BatchOrder with a given query_url, without waiting for order to be processed."""
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
                order_body = generate_order_body_from_query(ORDER_BODY_JSON, identifiers)
                send_post_request_to_batch_order_and_validate_response(order_body)
                break

        if "@odata.nextLink" in response and len(identifiers) < variables["parallel_quota"]:
            print(
                f"All products have been loaded to a list. Going to another link for more products: "
                f"{response['@odata.nextLink']}")
            response = get_response_from_next_link(response["@odata.nextLink"])
        elif "links" in response and len(identifiers) < variables["parallel_quota"]:
            for link in response["links"]:
                if link["rel"] == "next":
                    print(
                        f"All products have been loaded to a list. Going to another link for more products: "
                        f"{link['href']}")
                    response = get_response_from_next_link(link["href"])
        else:
            break


def create_batch_order_with_query_new_orders(variables: json, response: json, identifiers: list) -> None:
    """Option 2 - Creates new BatchOrder with a given query_url, with waiting for order to be processed."""
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
                order_body = generate_order_body_from_query(ORDER_BODY_JSON, identifiers)
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
    """Modifies query_url variable to take into account 'hours' variable specified by the user."""
    with open(f"{PWD}/jsons/query_details.json", "r+") as jsonFile:
        data = json.load(jsonFile)
        query_url = data["query_url"]
        current_date = datetime.datetime.now()
        earlier_date = str(current_date - datetime.timedelta(hours=hours))
        current_date = str(current_date)
        current_date = add_timezone_chars_to_date(current_date)
        earlier_date = add_timezone_chars_to_date(earlier_date)

        if "/stac/" in query_url:
            params = {"datetime": f"{earlier_date}/{current_date}"}
            url_parts = urllib.parse.urlparse(query_url)
            query = dict(urllib.parse.parse_qsl(url_parts.query))
            query.update(params)
            query_url = url_parts._replace(query=urllib.parse.urlencode(query)).geturl()
        else:
            res = get_date_from_query(query_url, "ContentDate/Start%20le%2", ")%20and%20(Online")
            query_url = query_url.replace(res, current_date)

            res2 = get_date_from_query(query_url, "ContentDate/Start%20ge%2", "%20and%20ContentDate")
            query_url = query_url.replace(res2, earlier_date)

        data["query_url"] = query_url
        jsonFile.seek(0)
        json.dump(data, jsonFile)
        jsonFile.truncate()


def check_order_details(order_id: int) -> None:
    """Option 3 - Outputs json from BatchOrder(order_id)"""
    response = requests.get(f"https://{KEYCLOAK_ORDERING_JSON['host']}/odata/v1/BatchOrder({order_id})",
                            headers=generate_headers(ordering_keycloak, KEYCLOAK_ORDERING_JSON),
                            verify=False)
    print(response.json())
