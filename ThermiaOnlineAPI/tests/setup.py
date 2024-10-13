from datetime import datetime, timedelta
import os
from typing import List

from .utils import match_lists_in_any_order, parse_debug_file

from .. import Thermia
from ..api.ThermiaAPI import (
    AZURE_AUTH_AUTHORIZE_URL,
    AZURE_AUTH_CONFIRM_URL,
    AZURE_AUTH_GET_TOKEN_URL,
    AZURE_SELF_ASSERTED_URL,
)
from ..const import THERMIA_CONFIG_URL
from ..model.HeatPump import ThermiaHeatPump

THERMIA_TEST_URL = "https://thermia-api-url"


def __mock_auth_requests(requests_mock):
    requests_mock.get(THERMIA_CONFIG_URL, json={"apiBaseUrl": THERMIA_TEST_URL})
    requests_mock.get(
        AZURE_AUTH_AUTHORIZE_URL,
        text='var SETTINGS = {"transId": "key=some-transaction-id-value", "csrf": "some-csrf-value"};',
    )
    requests_mock.post(AZURE_SELF_ASSERTED_URL, text="")
    requests_mock.get(
        AZURE_AUTH_CONFIRM_URL,
        json={},
    )
    requests_mock.post(
        AZURE_AUTH_GET_TOKEN_URL,
        json={
            "access_token": "some-access-token",
            "expires_on": (datetime.now() + timedelta(hours=6)).timestamp(),
            "refresh_token": "some-refresh-token",
        },
    )


def __mock_data_requests(requests_mock, test_data_file: str):
    absolute_path = os.path.dirname(os.path.abspath(__file__))
    test_data = parse_debug_file(f"{absolute_path}/debug_files/{test_data_file}")

    requests_mock.get(
        f"{THERMIA_TEST_URL}/api/v1/InstallationsInfo/own",
        json=[{**test_data["device_data"], "id": "test-id"}],
    )
    requests_mock.get(
        f"{THERMIA_TEST_URL}/api/v1/installations/test-id",
        json=test_data["info"],
    )
    requests_mock.get(
        f"{THERMIA_TEST_URL}/api/v1/installationstatus/test-id/status",
        json=test_data["status"],
    )
    requests_mock.get(
        f"{THERMIA_TEST_URL}/api/v1/Registers/Installations/test-id/Groups/REG_GROUP_TEMPERATURES",
        json=test_data["groups"]["REG_GROUP_TEMPERATURES"],
    )
    requests_mock.get(
        f"{THERMIA_TEST_URL}/api/v1/Registers/Installations/test-id/Groups/REG_GROUP_OPERATIONAL_STATUS",
        json=test_data["groups"]["REG_GROUP_OPERATIONAL_STATUS"],
    )
    requests_mock.get(
        f"{THERMIA_TEST_URL}/api/v1/Registers/Installations/test-id/Groups/REG_GROUP_OPERATIONAL_TIME",
        json=test_data["groups"]["REG_GROUP_OPERATIONAL_TIME"],
    )
    requests_mock.get(
        f"{THERMIA_TEST_URL}/api/v1/Registers/Installations/test-id/Groups/REG_GROUP_OPERATIONAL_OPERATION",
        json=test_data["groups"]["REG_GROUP_OPERATIONAL_OPERATION"],
    )
    requests_mock.get(
        f"{THERMIA_TEST_URL}/api/v1/Registers/Installations/test-id/Groups/REG_GROUP_HOT_WATER",
        json=test_data["groups"]["REG_GROUP_HOT_WATER"],
    )
    requests_mock.get(
        f"{THERMIA_TEST_URL}/api/v1/installation/test-id/events?onlyActiveAlarms=false",
        json=[],
    )


def setup_thermia_and_perform_basic_tests(
    requests_mock,
    test_data_file: str,
    expected_model: str,
    expected_model_id: str,
    expected_available_operational_modes: List[str],
    expected_available_operational_statuses: List[str],
    expected_available_power_statuses: List[str],
    expected_is_operation_mode_read_only: bool = False,
) -> ThermiaHeatPump:
    __mock_auth_requests(requests_mock)
    __mock_data_requests(requests_mock, test_data_file)

    thermia = Thermia("username", "password")

    assert thermia.connected == True

    heat_pump = thermia.heat_pumps[0]

    assert heat_pump.model == expected_model
    assert heat_pump.model_id == expected_model_id
    assert match_lists_in_any_order(
        heat_pump.available_operation_modes, expected_available_operational_modes
    )
    assert heat_pump.is_operation_mode_read_only == expected_is_operation_mode_read_only
    assert match_lists_in_any_order(
        heat_pump.available_operational_statuses,
        expected_available_operational_statuses,
    )
    assert match_lists_in_any_order(
        heat_pump.available_power_statuses, expected_available_power_statuses
    )

    return heat_pump
