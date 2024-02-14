import datetime
import re
import unittest
from unittest.mock import MagicMock, patch

from parameterized import parameterized

from auth import KeycloakToken, generate_headers, get_keycloak_response
from tests.data import (CATALOGUE_KEYCLOAK_DATA, CATALOGUE_URL, IDENTIFIERS,
                        KEYCLOAK_RESPONSE, ORDER_BODY, ORDER_CREATED,
                        ORDERING_KEYCLOAK_DATA, QUERY_RESPONSE,
                        STAC_CATALOGUE_URL)
from utils import (add_timezone_chars_to_date, cls,
                   generate_order_body_from_query, get_date_from_query,
                   get_response_from_next_link,
                   send_post_request_to_batch_order_and_validate_response)


class TestScript(unittest.TestCase):

    @parameterized.expand(
        [
            ["ns", "clear"],
            ["nt", "cls"],
        ]
    )
    @patch("utils.os")
    def test_cls(self, name, expected_value, mock_os):
        mock_os.system = MagicMock()
        mock_os.name = name
        cls()
        mock_os.system.assert_called_once_with(expected_value)

    def test_generate_order_body_from_query(self) -> None:
        generated_body = generate_order_body_from_query(ORDER_BODY, IDENTIFIERS)
        assert generated_body["IdentifierList"] == IDENTIFIERS

    @patch("utils.generate_headers", return_value={"d": "s"})
    @patch("utils.requests")
    def test_send_post_request_to_batch_order_and_validate_response(
        self, mock_requests, mock_generate_headers
    ):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = ORDER_CREATED

        mock_requests.post.return_value = mock_response

        response = send_post_request_to_batch_order_and_validate_response(
            {"d": "s"}
        ).json()
        self.assertEqual(response, ORDER_CREATED)

    @parameterized.expand(
        [
            [CATALOGUE_URL],
            [STAC_CATALOGUE_URL],
        ]
    )
    @patch("utils.generate_headers", return_value={"d": "s"})
    @patch("utils.requests")
    def test_get_response_from_next_link(
        self, catalogue_url, mock_requests, mock_generate_headers
    ):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = QUERY_RESPONSE

        mock_requests.get.return_value = mock_response

        response = get_response_from_next_link(catalogue_url)

        assert isinstance(response, dict)
        assert response == QUERY_RESPONSE

    def test_add_timezone_chars_to_date(self):
        current_date = datetime.datetime.now()
        current_date = add_timezone_chars_to_date(str(current_date))
        assert " " not in current_date

    def test_get_date_from_query(self):
        pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$"
        res = get_date_from_query(
            CATALOGUE_URL, "ContentDate/Start%20le%2", ")%20and%20(Online"
        )
        assert re.match(pattern, res)

    @parameterized.expand(
        [
            [ORDERING_KEYCLOAK_DATA],
            [CATALOGUE_KEYCLOAK_DATA],
        ]
    )
    @patch(
        "auth.get_keycloak_response",
        return_value={"access_token": "token", "expires_in": datetime.datetime.now()},
    )
    def test_generate_headers(self, keycloak_data, mock_get_keycloak_response):
        keycloak_token = KeycloakToken()
        keycloak_token.generation_date = datetime.datetime.now()
        keycloak_token.expiration_date = datetime.datetime.now() + datetime.timedelta(
            seconds=60
        )

        headers = generate_headers(keycloak_token, keycloak_data)
        assert (
            all(
                param in headers
                for param in [
                    "Authorization",
                    "Content-Type",
                    "Accept",
                    "Accept-Encoding",
                    "Connection",
                    "Host",
                ]
            )
            if "host" in keycloak_data
            else all(param in headers for param in ["Authorization", "Content-Type"])
        )

    @patch("auth.requests")
    def test_get_keycloak_response(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = KEYCLOAK_RESPONSE

        mock_requests.post.return_value = mock_response

        response = get_keycloak_response(CATALOGUE_KEYCLOAK_DATA)
        assert response == KEYCLOAK_RESPONSE


if __name__ == "__main__":
    unittest.main()
