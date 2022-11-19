import logging
from collections import ChainMap
from datetime import datetime, timedelta
import requests
import urllib.parse
import json
from base64 import urlsafe_b64encode, urlsafe_b64decode
import hashlib
import random
import string

from ThermiaOnlineAPI.const import (
    REG_GROUP_HOT_WATER,
    REG_GROUP_OPERATIONAL_OPERATION,
    REG_GROUP_OPERATIONAL_STATUS,
    REG_GROUP_OPERATIONAL_TIME,
    REG_GROUP_TEMPERATURES,
    REGISTER_GROUPS,
    THERMIA_API_CONFIG_URLS_BY_API_TYPE,
    THERMIA_INSTALLATION_PATH,
    THERMIA_GENESIS_API_AUTH_URL,
)


from ..exceptions.AuthenticationException import AuthenticationException
from ..exceptions.NetworkException import NetworkException
from ..model.HeatPump import ThermiaHeatPump

_LOGGER = logging.getLogger(__name__)


class ThermiaAPI:
    def __init__(self, email, password, api_type):
        self.__email = email
        self.__password = password
        self.__token = None
        self.__token_valid_to = None
        self.__api_type = api_type
        self.__refresh_token_valid_to = None
        self.__refresh_token = None

        self.__default_request_headers = {
            "Authorization": "Bearer ",
            "Content-Type": "application/json",
        }

        if api_type not in THERMIA_API_CONFIG_URLS_BY_API_TYPE:
            raise ValueError("Unknown device type: " + api_type)

        self.__api_config_url = THERMIA_API_CONFIG_URLS_BY_API_TYPE[api_type]

        self.configuration = self.__fetch_configuration()
        self.authenticated = self.__authenticate()

    def base64UrlEncode(self, data):
        return urlsafe_b64encode(data).rstrip(b'=')

    def base64UrlDecode(self, base64Url):
        return urlsafe_b64decode(base64Url + '=' * (4 - len(base64Url) % 4))

    def generate_Challenge(self, length):
        characters = string.ascii_letters + string.digits
        challenge = ''.join(random.choice(characters) for i in range(length))
        return challenge

    def get_devices(self):
        self.__check_token_validity()

        url = self.configuration["apiBaseUrl"] + \
            "/api/v1/InstallationsInfo/own"
        request = requests.get(url, headers=self.__default_request_headers)
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

        url = self.configuration["apiBaseUrl"] + \
            "/api/v1/installations/" + device_id
        request = requests.get(url, headers=self.__default_request_headers)
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
        request = requests.get(url, headers=self.__default_request_headers)
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
        request = requests.get(url, headers=self.__default_request_headers)
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
        request = requests.get(url, headers=self.__default_request_headers)
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
        request = requests.get(url, headers=self.__default_request_headers)
        status = request.status_code

        if status != 200:
            _LOGGER.error(
                "Error in historical data for specific register. " +
                str(status)
            )
            return None

        return request.json()

    def get_all_available_groups(self, installation_profile_id: int):
        self.__check_token_validity()

        url = self.configuration["apiBaseUrl"] + \
            "/api/v1/installationprofiles/" + \
            str(installation_profile_id) + "/groups"

        request = requests.get(url, headers=self.__default_request_headers)
        status = request.status_code

        if status != 200:
            _LOGGER.error("Error in getting available groups. " + str(status))
            return None

        return request.json()

    def get__group_temperatures(self, device_id: str):
        return self.__get_register_group(device_id, REG_GROUP_TEMPERATURES)

    def get__group_operational_status(self, device_id: str):
        register_data = self.__get_register_group(
            device_id, REG_GROUP_OPERATIONAL_STATUS
        )

        data = [
            d
            for d in register_data
            if d["registerName"] == "REG_OPERATIONAL_STATUS_PRIO1"
        ]

        if len(data) != 1:
            # Operation operational status not supported
            return None

        data = data[0]

        current_operation_mode_value = int(data.get("registerValue"))
        operation_modes_data = data.get("valueNames")

        if operation_modes_data is not None:
            operation_modes_map = map(
                lambda values: {
                    values.get("value"): values.get("name").split("REG_VALUE_STATUS_")[
                        1
                    ],
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

    def get__group_operational_time(self, device_id: str):
        return self.__get_register_group(device_id, REG_GROUP_OPERATIONAL_TIME)

    def get_group_operational_operation(self, device: ThermiaHeatPump):
        register_data = self.__get_register_group(
            device.id, REG_GROUP_OPERATIONAL_OPERATION
        )

        data = [d for d in register_data if d["registerName"]
                == "REG_OPERATIONMODE"]

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

    def get_group_hot_water(self, device: ThermiaHeatPump):
        register_data = self.__get_register_group(
            device.id, REG_GROUP_HOT_WATER)

        data = [d for d in register_data if d["registerName"]
                == "REG_HOT_WATER_STATUS"]

        if len(data) == 0:
            # Hot water switch not supported
            return None

        data = data[0]

        device.set_register_index_hot_water_switch(data["registerIndex"])

        current_switch_state = int(data.get("registerValue"))
        switch_states_data = data.get("valueNames")

        if switch_states_data is not None and len(switch_states_data) == 2:
            return current_switch_state

        return None

    def set_temperature(self, device: ThermiaHeatPump, temperature):
        device_temperature_register_index = device.get_register_indexes()[
            "temperature"]
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
        device_hot_water_switch_state_register_index = device.get_register_indexes()[
            "hot_water_switch"
        ]
        if device_hot_water_switch_state_register_index is None:
            _LOGGER.error(
                "Error setting device's hot water switch state. No hot water switch register index."
            )
            return

        self.__set_register_value(
            device, device_hot_water_switch_state_register_index, state
        )

    def get_register_group_json(self, device_id: str, register_group):
        return self.__get_register_group(device_id, register_group)

    def __get_register_group(self, device_id: str, register_group: REGISTER_GROUPS):
        self.__check_token_validity()

        url = (
            self.configuration["apiBaseUrl"]
            + THERMIA_INSTALLATION_PATH
            + str(device_id)
            + "/Groups/"
            + register_group
        )
        request = requests.get(url, headers=self.__default_request_headers)
        status = request.status_code

        if status != 200:
            _LOGGER.error(
                "Error in getting device's register group: "
                + register_group
                + ", Status: "
                + str(status)
            )
            return None

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

        request = requests.post(
            url, headers=self.__default_request_headers, json=body)

        status = request.status_code
        if status != 200:
            _LOGGER.error(
                "Error setting register "
                + str(register_index)
                + " value. "
                + str(status)
            )

    def __fetch_configuration(self):
        request = requests.get(self.__api_config_url)
        status = request.status_code

        if status != 200:
            _LOGGER.error("Error fetching API configuration. " + str(status))
            raise NetworkException("Error fetching API configuration.", status)

        return request.json()

    def __authenticatice_Classic(self):
        auth_url = self.configuration["authApiBaseUrl"] + "/api/v1/Jwt/login"
        json = {
            "userName": self.__email,
            "password": self.__password,
            "rememberMe": True,
        }

        request_auth = requests.post(auth_url, json=json)
        status = request_auth.status_code

        if status != 200:
            _LOGGER.error(
                "Authentication request failed, please check credentials. "
                + str(status)
            )
            raise AuthenticationException(
                "Authentication request failed, please check credentials.", status
            )

        auth_data = request_auth.json()

        token_valid_to = auth_data.get("tokenValidToUtc").split(".")[0]
        datetime_object = datetime.strptime(
            token_valid_to, "%Y-%m-%dT%H:%M:%S")
        token_valid_to = datetime_object.timestamp()

        self.__token = auth_data.get("token")
        self.__token_valid_to = token_valid_to

        self.__default_request_headers = {
            "Authorization": "Bearer " + self.__token,
            "Content-Type": "application/json",
        }

        _LOGGER.info("Authentication was successful, token set.")
        return True

    def __authenticate(self, refresh=False):
        if self.__api_type == "genesis":
            return self.__authenticate_Genesis(refresh)
        else:
            return self.__authenticatice_Classic()


    def __authenticate_Genesis(self,refresh):
        if(refresh):
            Headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        
            _data = "client_id=09ea4903-9e95-45fe-ae1f-e3b7d32fa385&redirect_uri=https%3A%2F%2Fonline-genesis.thermia.se%2Flogin&scope=09ea4903-9e95-45fe-ae1f-e3b7d32fa385"
            _data += "&refresh_token=" + self.__refresh_token
            _data += "&grant_type=refresh_token"

            uri = THERMIA_GENESIS_API_AUTH_URL + "oauth2/v2.0/token"
            
            request_token = requests.post(uri, headers=Headers, data=_data)
        else:
            code_Challenge = self.generate_Challenge(43)

            request_auth = requests.get(THERMIA_GENESIS_API_AUTH_URL + "oauth2/v2.0/authorize",
                {"client_id":"09ea4903-9e95-45fe-ae1f-e3b7d32fa385",
                "scope":"09ea4903-9e95-45fe-ae1f-e3b7d32fa385",
                "redirect_uri":"https://online-genesis.thermia.se/login",
                "response_type":"code", 
                "code_challenge":str(self.base64UrlEncode(hashlib.sha256(code_Challenge.encode('utf-8')).digest()),'utf-8'),
                "code_challenge_method":"S256"
                }
            )
            
            stateCode = ""
            csrf_token = ""
            
            a = request_auth.text

            if request_auth.status_code == 200:
                csrf_token = a[a.find('"csrf":"')+8:a.find('"',a.find('"csrf":"')+8)]
                stateCode = a[a.find('StateProperties=')+16:a.find('"',a.find('StateProperties=')+16)]
            else:
                _LOGGER.error("Error fetching API authorization. " + str(request_auth.reason))
                raise NetworkException("Error fetching API authorization.", request_auth.reason)
            

            Headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
            Headers["X-Csrf-Token"] = csrf_token

            _data = "request_type=RESPONSE&signInName=" + urllib.parse.quote(self.__email) + "&password=" + self.__password

            uri = THERMIA_GENESIS_API_AUTH_URL + "SelfAsserted?tx=StateProperties="
            uri += stateCode + "&p=B2C_1A_SignUpOrSigninOnline"
            request_self_asserted = requests.post(uri, headers=Headers, data=_data, cookies=request_auth.cookies)

            if request_self_asserted.status_code !=200 or '{"status":"400"' in request_self_asserted.text: #authentication failed
                _LOGGER.error("Error in API authencation. Wrong credentials " + str(request_self_asserted.text))
                raise NetworkException("Error in API authencation. Wrong credentials", request_self_asserted.text)

            Cookies = request_self_asserted.cookies
            cookie_obj = requests.cookies.create_cookie(name="x-ms-cpim-csrf",value=request_auth.cookies.get("x-ms-cpim-csrf"))
            Cookies.set_cookie(cookie_obj)
            
            uri = THERMIA_GENESIS_API_AUTH_URL + "api/CombinedSigninAndSignup/confirmed?csrf_token="
            uri += csrf_token + "&p=B2C_1A_SignUpOrSigninOnline"
            uri += "&tx=StateProperties=" + stateCode
            uri += "&p=B2C_1A_SignUpOrSigninOnline"

            request_confirmed = requests.get(uri,cookies=Cookies)

            Headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
            

            _data = "client_id=09ea4903-9e95-45fe-ae1f-e3b7d32fa385&redirect_uri=https%3A%2F%2Fonline-genesis.thermia.se%2Flogin&scope=09ea4903-9e95-45fe-ae1f-e3b7d32fa385"
            _data += "&code=" + request_confirmed.url.split("code=")[1]
            _data += "&code_verifier=" + code_Challenge
            _data += "&grant_type=authorization_code"

            uri = THERMIA_GENESIS_API_AUTH_URL + "oauth2/v2.0/token"
            
            request_token = requests.post(uri, headers=Headers, data=_data)

            status = 200

            if status != 200:
                _LOGGER.error(
                    "Authentication request failed, please check credentials. "
                    + str(status)
                )
                raise AuthenticationException(
                    "Authentication request failed, please check credentials.", status
                )

        token_data = json.loads(request_token.text)

        self.__token = token_data["access_token"]
        self.__token_valid_to = token_data["expires_on"]
        #refresh token valid for 24h
        self.__refresh_token_valid_to = (datetime.now() + timedelta(days=1)).timestamp()
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
        ):
            _LOGGER.info("Token expired, re-authenticating.")
            self.authenticated = self.__authenticate((self.__refresh_token_valid_to > datetime.now().timestamp()))
            