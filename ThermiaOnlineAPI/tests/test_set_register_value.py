import unittest
from unittest.mock import MagicMock, patch
import requests

from ThermiaOnlineAPI.api.ThermiaAPI import ThermiaAPI
from ThermiaOnlineAPI.exceptions.NetworkException import NetworkException
from ThermiaOnlineAPI.model.HeatPump import ThermiaHeatPump


class TestSetRegisterValue(unittest.TestCase):
    @patch.object(ThermiaAPI, "_ThermiaAPI__fetch_configuration")
    @patch.object(ThermiaAPI, "_ThermiaAPI__authenticate")
    def test_set_register_value_success(self, mock_auth, mock_fetch_config):
        mock_fetch_config.return_value = {"apiBaseUrl": "https://test.thermia.se"}
        mock_auth.return_value = True
        api = ThermiaAPI("test@example.com", "password")

        mock_device = MagicMock(spec=ThermiaHeatPump)
        mock_device.id = "12345"

        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200

        with patch.object(ThermiaAPI, "_ThermiaAPI__check_token_validity"):
            with patch.object(api._ThermiaAPI__session, "post", return_value=mock_response):
                api.set_register_value(mock_device, 100, 21)

    @patch.object(ThermiaAPI, "_ThermiaAPI__fetch_configuration")
    @patch.object(ThermiaAPI, "_ThermiaAPI__authenticate")
    def test_set_register_value_non_200_raises_network_exception(
        self, mock_auth, mock_fetch_config
    ):
        mock_fetch_config.return_value = {"apiBaseUrl": "https://test.thermia.se"}
        mock_auth.return_value = True
        api = ThermiaAPI("test@example.com", "password")

        mock_device = MagicMock(spec=ThermiaHeatPump)
        mock_device.id = "12345"

        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with patch.object(ThermiaAPI, "_ThermiaAPI__check_token_validity"):
            with patch.object(api._ThermiaAPI__session, "post", return_value=mock_response):
                with self.assertRaises(NetworkException) as ctx:
                    api.set_register_value(mock_device, 100, 21)
                self.assertEqual(ctx.exception.status, 500)

    @patch.object(ThermiaAPI, "_ThermiaAPI__fetch_configuration")
    @patch.object(ThermiaAPI, "_ThermiaAPI__authenticate")
    def test_set_register_value_request_exception_raises_network_exception(
        self, mock_auth, mock_fetch_config
    ):
        mock_fetch_config.return_value = {"apiBaseUrl": "https://test.thermia.se"}
        mock_auth.return_value = True
        api = ThermiaAPI("test@example.com", "password")

        mock_device = MagicMock(spec=ThermiaHeatPump)
        mock_device.id = "12345"

        with patch.object(ThermiaAPI, "_ThermiaAPI__check_token_validity"):
            with patch.object(
                api._ThermiaAPI__session,
                "post",
                side_effect=requests.exceptions.ConnectionError("Connection aborted"),
            ):
                with self.assertRaises(NetworkException):
                    api.set_register_value(mock_device, 100, 21)


if __name__ == "__main__":
    unittest.main()
