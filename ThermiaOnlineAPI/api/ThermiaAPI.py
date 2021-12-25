import logging
from datetime import datetime
import requests

from ..model.WaterHeater import ThermiaWaterHeater

LOGGER = logging.getLogger(__name__)

DEFAULT_REQUEST_HEADERS = {"Authorization": "Bearer %s", "Content-Type": "application/json"}

THERMIA_API_CONFIG_URL = "https://online.thermia.se/api/configuration"

SET_REGISTER_VALUES = {
    "set_temperature": 50,
    "set_operation_mode": 51,
}

class ThermiaAPI():
    def __init__(self, email, password):
        self.__email = email
        self.__password = password
        self.__token = None
        self.__token_valid_to = None

        self.configuration = self.__fetch_configuration()
        self.authenticated = self.__authenticate()

    def get_devices(self):
        self.__check_token_validity()

        url = self.configuration['apiBaseUrl'] + "/api/v1/InstallationsInfo/own"
        request = requests.get(url, headers=DEFAULT_REQUEST_HEADERS)
        status = request.status_code
        LOGGER.info("Fetching devices. " + str(status))
        
        if status != 200:
            LOGGER.error("Error fetching devices. " + str(status))
            return []

        return request.json()

    def get_device_info(self, device):
        self.__check_token_validity()

        url = self.configuration['apiBaseUrl'] + "/api/v1/installations/" + str(device['id'])
        request = requests.get(url, headers=DEFAULT_REQUEST_HEADERS)
        status = request.status_code

        if status != 200:
            LOGGER.error("Error fetching device info. " + str(status))
            return None

        return request.json()

    def get_device_status(self, device):
        self.__check_token_validity()

        url = self.configuration['apiBaseUrl'] + "/api/v1/installationstatus/" + str(device['id']) + "/status"
        request = requests.get(url, headers=DEFAULT_REQUEST_HEADERS)
        status = request.status_code

        if status != 200:
            LOGGER.error("Error fetching device status. " + str(status))
            return None

        return request.json()

    def get_operation_mode(self, device):
        self.__check_token_validity()

        url = self.configuration['apiBaseUrl'] + "/api/v1/Registers/Installations/" + str(device['id']) + "/Groups/REG_GROUP_OPERATIONAL_OPERATION"
        request = requests.get(url, headers=DEFAULT_REQUEST_HEADERS)
        status = request.status_code

        if status != 200:
            LOGGER.error("Error in getting device's operation mode. " + str(status))
            return None

        data = request.json()[0]

        current_operation_mode = int(data.get("registerValue"))
        operation_modes_data = data.get("valueNames")

        if operation_modes_data is not None:
            operation_modes = list(map(lambda values: values.get("name").split("REG_VALUE_OPERATION_MODE_")[1], operation_modes_data))
            return {
                "current": operation_modes[current_operation_mode],
                "available": operation_modes
            }

        return None

    def set_temperature(self, device: ThermiaWaterHeater, temperature):
        self.__set_register_value(device, SET_REGISTER_VALUES["set_temperature"], temperature)

    def set_operation_mode(self, device: ThermiaWaterHeater, mode):
        operation_mode_int = device.available_operation_modes.index(mode)
        self.__set_register_value(device, SET_REGISTER_VALUES["set_operation_mode"], operation_mode_int)

    def __set_register_value(self, device: ThermiaWaterHeater, register_index: SET_REGISTER_VALUES, register_value: int):
        self.__check_token_validity()

        url = self.configuration['apiBaseUrl'] + "/api/v1/Registers/Installations/" + str(device.id) + "/Registers"
        body = {
            "registerIndex": register_index,
            "registerValue": register_value,
            "clientUuid": "api-client-uuid"
        }

        request =  requests.post(url, headers=DEFAULT_REQUEST_HEADERS, json=body)

        status = request.status_code
        if status != 200:
            LOGGER.error("Error setting register " + str(register_index) + " value. " + str(status))

    def __fetch_configuration(self):
        request = requests.get(THERMIA_API_CONFIG_URL)
        status = request.status_code

        if status != 200:
            LOGGER.error("Error fetching API configuration. " + str(status))
            raise Exception("Error fetching API configuration.", status)

        return request.json()

    def __authenticate(self):
        auth_url = self.configuration['authApiBaseUrl'] + "/api/v1/Jwt/login"
        json = {"userName": self.__email, "password": self.__password, "rememberMe": True}

        request_auth = requests.post(auth_url, json=json)
        status = request_auth.status_code

        if status != 200:
            LOGGER.error("Authentication request failed, please check credentials. " + str(status))
            raise Exception("Authentication request failed, please check credentials.", status)

        auth_data = request_auth.json()
        LOGGER.debug(str(auth_data))

        token_valid_to = auth_data.get("tokenValidToUtc").split(".")[0]
        datetime_object = datetime.strptime(token_valid_to, '%Y-%m-%dT%H:%M:%S')
        token_valid_to = datetime_object.timestamp()

        self.__token = auth_data.get("token")
        self.__token_valid_to = token_valid_to

        auth = DEFAULT_REQUEST_HEADERS.get("Authorization")
        auth = auth % self.__token
        DEFAULT_REQUEST_HEADERS["Authorization"] = auth

        LOGGER.info("Authentication was successful, token set.")
        return True

    def __check_token_validity(self):
        if self.__token_valid_to is None or self.__token_valid_to < datetime.now().timestamp():
            LOGGER.info("Token expired, reauthenticating.")
            self.authenticated = self.__authenticate()