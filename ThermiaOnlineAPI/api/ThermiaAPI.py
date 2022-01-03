import logging
from datetime import datetime
import requests


from ..exceptions.AuthenticationException import AuthenticationException
from ..exceptions.NetworkException import NetworkException
from ..model.HeatPump import ThermiaHeatPump

LOGGER = logging.getLogger(__name__)

THERMIA_API_CONFIG_URL = "https://online.thermia.se/api/configuration"
THERMIA_INSTALLATION_PATH = "/api/v1/Registers/Installations/"


class ThermiaAPI:
    def __init__(self, email, password):
        self.__email = email
        self.__password = password
        self.__token = None
        self.__token_valid_to = None

        self.__default_request_headers = {
            "Authorization": "Bearer ",
            "Content-Type": "application/json",
        }

        self.configuration = self.__fetch_configuration()
        self.authenticated = self.__authenticate()

    def get_devices(self):
        self.__check_token_validity()

        url = self.configuration["apiBaseUrl"] + "/api/v1/InstallationsInfo/own"
        request = requests.get(url, headers=self.__default_request_headers)
        status = request.status_code
        LOGGER.info("Fetching devices. " + str(status))

        if status != 200:
            LOGGER.error("Error fetching devices. " + str(status))
            return []

        return request.json()

    def get_device_info(self, device):
        self.__check_token_validity()

        url = (
            self.configuration["apiBaseUrl"]
            + "/api/v1/installations/"
            + str(device["id"])
        )
        request = requests.get(url, headers=self.__default_request_headers)
        status = request.status_code

        if status != 200:
            LOGGER.error("Error fetching device info. " + str(status))
            return None

        return request.json()

    def get_device_status(self, device):
        self.__check_token_validity()

        url = (
            self.configuration["apiBaseUrl"]
            + "/api/v1/installationstatus/"
            + str(device["id"])
            + "/status"
        )
        request = requests.get(url, headers=self.__default_request_headers)
        status = request.status_code

        if status != 200:
            LOGGER.error("Error fetching device status. " + str(status))
            return None

        return request.json()

    def get_temperature_status(self, device: ThermiaHeatPump):
        self.__check_token_validity()

        url = (
            self.configuration["apiBaseUrl"]
            + THERMIA_INSTALLATION_PATH
            + str(device.id)
            + "/Groups/REG_GROUP_TEMPERATURES"
        )
        request = requests.get(url, headers=self.__default_request_headers)
        status = request.status_code

        if status != 200:
            LOGGER.error("Error in getting device's temperature status. " + str(status))
            return None

        device_temperature_register_index = device.get_register_indexes()["temperature"]
        if device_temperature_register_index is None:
            LOGGER.error(
                "Error in getting device's temperature status. No temperature register index."
            )
            return None

        data = [
            d
            for d in request.json()
            if d["registerIndex"] == device_temperature_register_index
        ]

        if len(data) == 0:
            # Temperature status not supported
            return None

        data = data[0]

        return {
            "minValue": data["minValue"],
            "maxValue": data["maxValue"],
            "step": data["step"],
        }

    def get_operation_mode(self, device: ThermiaHeatPump):
        self.__check_token_validity()

        url = (
            self.configuration["apiBaseUrl"]
            + THERMIA_INSTALLATION_PATH
            + str(device.id)
            + "/Groups/REG_GROUP_OPERATIONAL_OPERATION"
        )
        request = requests.get(url, headers=self.__default_request_headers)
        status = request.status_code

        if status != 200:
            LOGGER.error("Error in getting device's operation mode. " + str(status))
            return None

        data = [d for d in request.json() if d["registerName"] == "REG_OPERATIONMODE"]

        if len(data) == 0:
            # Operation mode not supported
            return None

        data = data[0]

        device.set_register_index_operation_mode(data["registerIndex"])

        current_operation_mode = int(data.get("registerValue"))
        operation_modes_data = data.get("valueNames")

        if operation_modes_data is not None:
            operation_modes = list(
                map(
                    lambda values: values.get("name").split(
                        "REG_VALUE_OPERATION_MODE_"
                    )[1],
                    operation_modes_data,
                )
            )
            return {
                "current": operation_modes[current_operation_mode],
                "available": operation_modes,
            }

        return None

    def set_temperature(self, device: ThermiaHeatPump, temperature):
        device_temperature_register_index = device.get_register_indexes()["temperature"]
        if device_temperature_register_index is None:
            LOGGER.error(
                "Error setting device's temperature. No temperature register index."
            )
            return

        self.__set_register_value(
            device, device_temperature_register_index, temperature
        )

    def set_operation_mode(self, device: ThermiaHeatPump, mode):
        operation_mode_int = device.available_operation_modes.index(mode)

        device_operation_mode_register_index = device.get_register_indexes()[
            "operation_mode"
        ]
        if device_operation_mode_register_index is None:
            LOGGER.error(
                "Error setting device's operation mode. No operation mode register index."
            )
            return

        self.__set_register_value(
            device, device_operation_mode_register_index, operation_mode_int
        )

    def __set_register_value(
        self, device: ThermiaHeatPump, register_index: int, register_value: int
    ):
        self.__check_token_validity()

        url = (
            self.configuration["apiBaseUrl"]
            + THERMIA_INSTALLATION_PATH
            + str(device.id)
            + "/Registers"
        )
        body = {
            "registerIndex": register_index,
            "registerValue": register_value,
            "clientUuid": "api-client-uuid",
        }

        request = requests.post(url, headers=self.__default_request_headers, json=body)

        status = request.status_code
        if status != 200:
            LOGGER.error(
                "Error setting register "
                + str(register_index)
                + " value. "
                + str(status)
            )

    def __fetch_configuration(self):
        request = requests.get(THERMIA_API_CONFIG_URL)
        status = request.status_code

        if status != 200:
            LOGGER.error("Error fetching API configuration. " + str(status))
            raise NetworkException("Error fetching API configuration.", status)

        return request.json()

    def __authenticate(self):
        auth_url = self.configuration["authApiBaseUrl"] + "/api/v1/Jwt/login"
        json = {
            "userName": self.__email,
            "password": self.__password,
            "rememberMe": True,
        }

        request_auth = requests.post(auth_url, json=json)
        status = request_auth.status_code

        if status != 200:
            LOGGER.error(
                "Authentication request failed, please check credentials. "
                + str(status)
            )
            raise AuthenticationException(
                "Authentication request failed, please check credentials.", status
            )

        auth_data = request_auth.json()
        LOGGER.debug(str(auth_data))

        token_valid_to = auth_data.get("tokenValidToUtc").split(".")[0]
        datetime_object = datetime.strptime(token_valid_to, "%Y-%m-%dT%H:%M:%S")
        token_valid_to = datetime_object.timestamp()

        self.__token = auth_data.get("token")
        self.__token_valid_to = token_valid_to

        self.__default_request_headers = {
            "Authorization": "Bearer " + self.__token,
            "Content-Type": "application/json",
        }

        LOGGER.info("Authentication was successful, token set.")
        return True

    def __check_token_validity(self):
        if (
            self.__token_valid_to is None
            or self.__token_valid_to < datetime.now().timestamp()
        ):
            LOGGER.info("Token expired, reauthenticating.")
            self.authenticated = self.__authenticate()
