import unittest
from unittest.mock import MagicMock, patch
import requests

from ThermiaOnlineAPI.api.ThermiaAPI import ThermiaAPI
from ThermiaOnlineAPI.exceptions.NetworkException import NetworkException


class TestRetryResilience(unittest.TestCase):
    @patch.object(ThermiaAPI, "_ThermiaAPI__fetch_configuration")
    @patch.object(ThermiaAPI, "_ThermiaAPI__authenticate")
    def test_request_retries_on_connection_reset_and_succeeds(
        self, mock_auth, mock_fetch_config
    ):
        mock_fetch_config.return_value = {"apiBaseUrl": "https://test.thermia.se"}
        mock_auth.return_value = True

        api = ThermiaAPI("test@example.com", "password")

        # Mock session to fail on first attempt with ConnectionResetError, then succeed
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.text = '{"success": true}'

        side_effects = [
            requests.exceptions.ConnectionError(
                ConnectionResetError(104, "Connection reset by peer")
            ),
            mock_response,
        ]

        with patch.object(api, "_create_session") as mock_create_session:
            mock_new_session = MagicMock()
            mock_new_session.post.side_effect = side_effects
            mock_create_session.return_value = mock_new_session
            api._ThermiaAPI__session = mock_new_session

            response = api._request_with_retry(
                "POST", "https://test.thermia.se/Registers", max_retries=3
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(mock_new_session.post.call_count, 2)

    @patch.object(ThermiaAPI, "_ThermiaAPI__fetch_configuration")
    @patch.object(ThermiaAPI, "_ThermiaAPI__authenticate")
    def test_request_raises_network_exception_when_all_retries_exhausted(
        self, mock_auth, mock_fetch_config
    ):
        mock_fetch_config.return_value = {"apiBaseUrl": "https://test.thermia.se"}
        mock_auth.return_value = True

        api = ThermiaAPI("test@example.com", "password")

        with patch.object(api, "_create_session") as mock_create_session:
            mock_session = MagicMock()
            mock_session.get.side_effect = requests.exceptions.ConnectionError(
                ConnectionResetError(104, "Connection reset by peer")
            )
            mock_create_session.return_value = mock_session
            api._ThermiaAPI__session = mock_session

            with self.assertRaises(NetworkException):
                api._request_with_retry(
                    "GET", "https://test.thermia.se/status", max_retries=3
                )


if __name__ == "__main__":
    unittest.main()
