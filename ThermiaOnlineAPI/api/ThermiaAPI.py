import logging
from collections import ChainMap
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter, Retry
from requests import cookies
import json
import hashlib
from typing import Dict, Optional

from ThermiaOnlineAPI.const import (
    REG_GROUP_HOT_WATER,
    REG_GROUP_OPERATIONAL_OPERATION,
    REG_GROUP_OPERATIONAL_STATUS,
    REG_GROUP_OPERATIONAL_TIME,
    REG_GROUP_TEMPERATURES,
    REG_HOT_WATER_STATUS,
    REG__HOT_WATER_BOOST,
    REG_OPERATIONMODE,
    THERMIA_API_CONFIG_URLS_BY_API_TYPE,
    THERMIA_AZURE_AUTH_URL,
    THERMIA_AZURE_AUTH_CLIENT_ID_AND_SCOPE,
    THERMIA_AZURE_AUTH_REDIRECT_URI,
    THERMIA_INSTALLATION_PATH,
)


from ..exceptions.AuthenticationException import AuthenticationException
from ..exceptions.NetworkException import NetworkException
from ..model.HeatPump import ThermiaHeatPump
from ..utils import utils

_LOGGER = logging.getLogger(__name__)

# Azure auth URLs
AZURE_AUTH_AUTHORIZE_URL = THERMIA_AZURE_AUTH_URL + "/oauth2/v2.0/authorize"
AZURE_AUTH_GET_TOKEN_URL = THERMIA_AZURE_AUTH_URL + "/oauth2/v2.0/token"
AZURE_SELF_ASSERTED_URL = THERMIA_AZURE_AUTH_URL + "/SelfAsserted"
AZURE_AUTH_CONFIRM_URL = (
    THERMIA_AZURE_AUTH_URL + "/api/CombinedSigninAndSignup/confirmed"
)

# Azure default headers
azure_auth_request_headers = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
}


class ThermiaAPI:
    def __init__(self, email, password, api_type):
        self.__email = email
        self.__password = password
        self.__token = None
        self.__token_valid_to = None
        self.__refresh_token_valid_to = None
        self.__refresh_token = None

        self.__default_request_headers = {
            "Authorization": "Bearer ",
            "Content-Type": "application/json",
        }

        self.__session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.__session.mount("https://", adapter)

        if api_type not in THERMIA_API_CONFIG_URLS_BY_API_TYPE:
            raise ValueError("Unknown device type: " + api_type)

        self.__api_config_url = THERMIA_API_CONFIG_URLS_BY_API_TYPE[api_type]

        self.configuration = self.__fetch_configuration()
        self.authenticated = self.__authenticate()

    def get_devices(self):
        self.__check_token_validity()

        url = self.configuration["apiBaseUrl"] + "/api/v1/InstallationsInfo/own"
        request = self.__session.get(url, headers=self.__default_request_headers)
        status = request.status_code

        if status != 200:
            _LOGGER.error("Error fetching devices. " + str(status))
            return []

        return request.json()

    def get_device_by_id(self, device_id: str):
        self.__check_token_validity()

        devices = self.get_devices()

        device = [d for d in devices if str(d["id"]) == device_id]

        if len(device) != 1:
            _LOGGER.error("Error getting device by id: " + str(device_id))
            return None

        return device[0]

    def get_device_info(self, device_id: str):
        self.__check_token_validity()

        url = self.configuration["apiBaseUrl"] + "/api/v1/installations/" + device_id
        request = self.__session.get(url, headers=self.__default_request_headers)
        status = request.status_code

        if status != 200:
            _LOGGER.error("Error fetching device info. " + str(status))
            return None

        return request.json()

    def get_device_status(self, device_id: str):
        self.__check_token_validity()

        url = (
            self.configuration["apiBaseUrl"]
            + "/api/v1/installationstatus/"
            + device_id
            + "/status"
        )
        request = self.__session.get(url, headers=self.__default_request_headers)
        status = request.status_code

        if status != 200:
            _LOGGER.error("Error fetching device status. " + str(status))
            return None

        return request.json()

    def get_all_alarms(self, device_id: str):
        self.__check_token_validity()

        url = (
            self.configuration["apiBaseUrl"]
            + "/api/v1/installation/"
            + str(device_id)
            + "/events?onlyActiveAlarms=false"
        )
        request = self.__session.get(url, headers=self.__default_request_headers)
        status = request.status_code

        if status != 200:
            _LOGGER.error("Error in getting device's alarms. " + str(status))
            return None

        return request.json()

    def get_historical_data_registers(self, device_id: str):
        self.__check_token_validity()

        url = (
            self.configuration["apiBaseUrl"]
            + "/api/v1/DataHistory/installation/"
            + str(device_id)
        )
        request = self.__session.get(url, headers=self.__default_request_headers)
        status = request.status_code

        if status != 200:
            _LOGGER.error("Error in historical data registers. " + str(status))
            return None

        return request.json()

    def get_historical_data(
        self, device_id: str, register_id, start_date_str, end_date_str
    ):
        self.__check_token_validity()

        url = (
            self.configuration["apiBaseUrl"]
            + "/api/v1/datahistory/installation/"
            + str(device_id)
            + "/register/"
            + str(register_id)
            + "/minute?periodStart="
            + start_date_str
            + "&periodEnd="
            + end_date_str
        )
        request = self.__session.get(url, headers=self.__default_request_headers)
        status = request.status_code

        if status != 200:
            _LOGGER.error(
                "Error in historical data for specific register. " + str(status)
            )
            return None

        return request.json()

    def get_all_available_groups(self, installation_profile_id: int):
        self.__check_token_validity()

        url = (
            self.configuration["apiBaseUrl"]
            + "/api/v1/installationprofiles/"
            + str(installation_profile_id)
            + "/groups"
        )

        request = self.__session.get(url, headers=self.__default_request_headers)
        status = request.status_code

        if status != 200:
            _LOGGER.error("Error in getting available groups. " + str(status))
            return None

        return request.json()

    def get__group_temperatures(self, device_id: str):
        return self.__get_register_group(device_id, REG_GROUP_TEMPERATURES)

    def get__group_operational_status(self, device_id: str):
        return self.__get_register_group(device_id, REG_GROUP_OPERATIONAL_STATUS)

    def get__group_operational_time(self, device_id: str):
        return self.__get_register_group(device_id, REG_GROUP_OPERATIONAL_TIME)

    def get_group_operational_operation(self, device: ThermiaHeatPump):
        register_data = self.__get_register_group(
            device.id, REG_GROUP_OPERATIONAL_OPERATION
        )

        data = [d for d in register_data if d["registerName"] == REG_OPERATIONMODE]

        if len(data) != 1:
            # Operation mode not supported
            return None

        data = data[0]

        device.set_register_index_operation_mode(data["registerIndex"])

        current_operation_mode_value = int(data.get("registerValue"))
        operation_modes_data = data.get("valueNames")

        if operation_modes_data is not None:
            operation_modes_map = map(
                lambda values: {
                    values.get("value"): values.get("name").split(
                        "REG_VALUE_OPERATION_MODE_"
                    )[1],
                },
                operation_modes_data,
            )
            operation_modes_list = list(operation_modes_map)
            operation_modes = ChainMap(*operation_modes_list)

            current_operation_mode = [
                name
                for value, name in operation_modes.items()
                if value == current_operation_mode_value
            ]
            if len(current_operation_mode) != 1:
                # Something has gone wrong or operation mode not supported
                return None

            return {
                "current": current_operation_mode[0],
                "available": operation_modes,
                "isReadOnly": data["isReadOnly"],
            }

        return None

    def __get_switch_register_index_and_value_from_group_by_register_name(
        self, register_group: list, register_name: str
    ):
        default_return_object = {
            "registerIndex": None,
            "registerValue": None,
        }

        switch_data_list = [
            d for d in register_group if d["registerName"] == register_name
        ]

        if len(switch_data_list) != 1:
            # Switch not supported
            return default_return_object

        switch_data: dict = switch_data_list[0]

        register_value = switch_data.get("registerValue")

        if register_value is None:
            return default_return_object

        # Validate that register is a switch
        switch_states_data = switch_data.get("valueNames")

        if switch_states_data is None or len(switch_states_data) != 2:
            return default_return_object

        return {
            "registerIndex": switch_data["registerIndex"],
            "registerValue": int(register_value),
        }

    def get_group_hot_water(self, device: ThermiaHeatPump) -> Dict[str, Optional[int]]:
        register_data: list = self.__get_register_group(device.id, REG_GROUP_HOT_WATER)

        hot_water_switch_data = (
            self.__get_switch_register_index_and_value_from_group_by_register_name(
                register_data, REG_HOT_WATER_STATUS
            )
        )
        hot_water_boost_switch_data = (
            self.__get_switch_register_index_and_value_from_group_by_register_name(
                register_data, REG__HOT_WATER_BOOST
            )
        )

        device.set_register_index_hot_water_switch(
            hot_water_switch_data["registerIndex"]
        )

        device.set_register_index_hot_water_boost_switch(
            hot_water_boost_switch_data["registerIndex"]
        )

        return {
            "hot_water_switch": hot_water_switch_data["registerValue"],
            "hot_water_boost_switch": hot_water_boost_switch_data["registerValue"],
        }

    def set_temperature(self, device: ThermiaHeatPump, temperature):
        device_temperature_register_index = device.get_register_indexes()["temperature"]
        if device_temperature_register_index is None:
            _LOGGER.error(
                "Error setting device's temperature. No temperature register index."
            )
            return

        self.__set_register_value(
            device, device_temperature_register_index, temperature
        )

    def set_operation_mode(self, device: ThermiaHeatPump, mode):
        if device.is_operation_mode_read_only:
            _LOGGER.error(
                "Error setting device's operation mode. Operation mode is read only."
            )
            return

        operation_mode_int = None

        for value, name in device.available_operation_mode_map.items():
            if name == mode:
                operation_mode_int = value

        if operation_mode_int is None:
            _LOGGER.error(
                "Error setting device's operation mode. Invalid operation mode."
            )
            return

        device_operation_mode_register_index = device.get_register_indexes()[
            "operation_mode"
        ]
        if device_operation_mode_register_index is None:
            _LOGGER.error(
                "Error setting device's operation mode. No operation mode register index."
            )
            return

        self.__set_register_value(
            device, device_operation_mode_register_index, operation_mode_int
        )

    def set_hot_water_switch_state(
        self, device: ThermiaHeatPump, state: int
    ):  # 0 - off, 1 - on
        register_index = device.get_register_indexes()["hot_water_switch"]
        if register_index is None:
            _LOGGER.error(
                "Error setting device's hot water switch state. No hot water switch register index."
            )
            return

        self.__set_register_value(device, register_index, state)

    def set_hot_water_boost_switch_state(
        self, device: ThermiaHeatPump, state: int
    ):  # 0 - off, 1 - on
        register_index = device.get_register_indexes()["hot_water_boost_switch"]
        if register_index is None:
            _LOGGER.error(
                "Error setting device's hot water boost switch state. No hot water boost switch register index."
            )
            return

        self.__set_register_value(device, register_index, state)

    def get_register_group_json(self, device_id: str, register_group: str) -> list:
        return self.__get_register_group(device_id, register_group)

    def set_register_value(
        self, device: ThermiaHeatPump, register_index: int, value: int
    ):
        self.__set_register_value(device, register_index, value)

    def __get_register_group(self, device_id: str, register_group: str) -> list:
        self.__check_token_validity()

        url = (
            self.configuration["apiBaseUrl"]
            + THERMIA_INSTALLATION_PATH
            + str(device_id)
            + "/Groups/"
            + register_group
        )
        request = self.__session.get(url, headers=self.__default_request_headers)
        status = request.status_code

        if status != 200:
            _LOGGER.error(
                "Error in getting device's register group: "
                + register_group
                + ", Status: "
                + str(status)
            )
            return []

        return request.json()

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

        request = self.__session.post(
            url, headers=self.__default_request_headers, json=body
        )

        status = request.status_code
        if status != 200:
            _LOGGER.error(
                "Error setting register "
                + str(register_index)
                + " value. "
                + str(status)
            )

    def __fetch_configuration(self):
        request = self.__session.get(self.__api_config_url)
        status = request.status_code

        if status != 200:
            _LOGGER.error("Error fetching API configuration. " + str(status))
            raise NetworkException("Error fetching API configuration.", status)

        return request.json()

    def __authenticate_refresh_token(self) -> Optional[str]:
        request_token__data = {
            "client_id": THERMIA_AZURE_AUTH_CLIENT_ID_AND_SCOPE,
            "redirect_uri": THERMIA_AZURE_AUTH_REDIRECT_URI,
            "scope": THERMIA_AZURE_AUTH_CLIENT_ID_AND_SCOPE,
            "refresh_token": self.__refresh_token,
            "grant_type": "refresh_token",
        }

        request_token = self.__session.post(
            AZURE_AUTH_GET_TOKEN_URL,
            headers=azure_auth_request_headers,
            data=request_token__data,
        )

        if request_token.status_code != 200:
            self.__refresh_token = None
            self.__refresh_token_valid_to = None

            error_text = (
                "Reauthentication request failed with previous refresh token. Status: "
                + str(request_token.status_code)
                + ", Response: "
                + request_token.text
            )
            _LOGGER.info(error_text)

            return None

        return request_token.text

    def __authenticate(self) -> bool:
        refresh_azure_token = self.__refresh_token_valid_to and (
            self.__refresh_token_valid_to > datetime.now().timestamp()
        )

        request_token_text = None

        if refresh_azure_token:  # Refresh token
            request_token_text = self.__authenticate_refresh_token()

        if request_token_text is None:  # New token, or refresh failed
            self.__token = None
            self.__token_valid_to = None

            code_challenge = utils.generate_challenge(43)

            request_auth__data = {
                "client_id": THERMIA_AZURE_AUTH_CLIENT_ID_AND_SCOPE,
                "scope": THERMIA_AZURE_AUTH_CLIENT_ID_AND_SCOPE,
                "redirect_uri": THERMIA_AZURE_AUTH_REDIRECT_URI,
                "response_type": "code",
                "code_challenge": str(
                    utils.base64_url_encode(
                        hashlib.sha256(code_challenge.encode("utf-8")).digest()
                    ),
                    "utf-8",
                ),
                "code_challenge_method": "S256",
            }

            request_auth = self.__session.get(
                AZURE_AUTH_AUTHORIZE_URL, data=request_auth__data
            )

            state_code = ""
            csrf_token = ""

            if request_auth.status_code == 200:
                settings_string = [
                    i
                    for i in request_auth.text.splitlines()
                    if i.startswith("var SETTINGS = ")
                ]
                if len(settings_string) > 0:
                    settings = json.loads(settings_string[0][15:-1])

                    state_code = str(settings["transId"]).split("=")[1]
                    csrf_token = settings["csrf"]
            else:
                _LOGGER.error(
                    "Error fetching authorization API. " + str(request_auth.reason)
                )
                raise NetworkException(
                    "Error fetching authorization API.", request_auth.reason
                )

            request_self_asserted__data = {
                "request_type": "RESPONSE",
                "signInName": self.__email,
                "password": self.__password,
            }

            request_self_asserted__query_params = {
                "tx": "StateProperties=" + state_code,
                "p": "B2C_1A_SignUpOrSigninOnline",
            }

            request_self_asserted = self.__session.post(
                AZURE_SELF_ASSERTED_URL,
                cookies=request_auth.cookies,
                data=request_self_asserted__data,
                headers={**azure_auth_request_headers, "X-Csrf-Token": csrf_token},
                params=request_self_asserted__query_params,
            )

            if (
                request_self_asserted.status_code != 200
                or '{"status":"400"' in request_self_asserted.text
            ):  # authentication failed
                _LOGGER.error(
                    "Error in API authencation. Wrong credentials "
                    + str(request_self_asserted.text)
                )
                raise NetworkException(
                    "Error in API authencation. Wrong credentials",
                    request_self_asserted.text,
                )

            request_confirmed__cookies = request_self_asserted.cookies
            cookie_obj = cookies.create_cookie(
                name="x-ms-cpim-csrf", value=request_auth.cookies.get("x-ms-cpim-csrf")
            )
            request_confirmed__cookies.set_cookie(cookie_obj)

            request_confirmed__params = {
                "csrf_token": csrf_token,
                "tx": "StateProperties=" + state_code,
                "p": "B2C_1A_SignUpOrSigninOnline",
            }

            request_confirmed = self.__session.get(
                AZURE_AUTH_CONFIRM_URL,
                cookies=request_confirmed__cookies,
                params=request_confirmed__params,
            )

            request_token__data = {
                "client_id": THERMIA_AZURE_AUTH_CLIENT_ID_AND_SCOPE,
                "redirect_uri": THERMIA_AZURE_AUTH_REDIRECT_URI,
                "scope": THERMIA_AZURE_AUTH_CLIENT_ID_AND_SCOPE,
                "code": request_confirmed.url.split("code=")[1],
                "code_verifier": code_challenge,
                "grant_type": "authorization_code",
            }

            request_token = self.__session.post(
                AZURE_AUTH_GET_TOKEN_URL,
                headers=azure_auth_request_headers,
                data=request_token__data,
            )

            if request_token.status_code != 200:
                error_text = (
                    "Authentication request failed, please check credentials. Status: "
                    + str(request_token.status_code)
                    + ", Response: "
                    + request_token.text
                )
                _LOGGER.error(error_text)
                raise AuthenticationException(error_text)

            request_token_text = request_token.text

        token_data = json.loads(request_token_text)

        self.__token = token_data["access_token"]
        self.__token_valid_to = token_data["expires_on"]

        # refresh token valid for 24h (maybe), but we refresh it every 6h for safety
        self.__refresh_token_valid_to = (
            datetime.now() + timedelta(hours=6)
        ).timestamp()
        self.__refresh_token = token_data.get("refresh_token")

        self.__default_request_headers = {
            "Authorization": "Bearer " + self.__token,
            "Content-Type": "application/json",
        }

        _LOGGER.info("Authentication was successful, token set.")

        return True

    def __check_token_validity(self):
        if (
            self.__token_valid_to is None
            or self.__token_valid_to < datetime.now().timestamp()
            or self.__refresh_token_valid_to is None
            or self.__refresh_token_valid_to < datetime.now().timestamp()
        ):
            _LOGGER.info("Token expired, re-authenticating.")
            self.authenticated = self.__authenticate()
