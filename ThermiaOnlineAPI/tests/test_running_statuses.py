import pytest

from .. import Thermia
from . import setup
from .utils import match_lists_in_any_order


def load_heat_pump(
    requests_mock, monkeypatch, test_data_file, register_name, value, presentation=None
):
    parse_debug_file = setup.parse_debug_file

    def parse_with_register_value(path):
        data = parse_debug_file(path)
        register = next(
            r
            for r in data["groups"]["REG_GROUP_OPERATIONAL_STATUS"]
            if r["registerName"] == register_name
        )
        register["registerValue"] = float(value)
        if presentation is not None:
            register["presentation"] = presentation
        return data

    monkeypatch.setattr(setup, "parse_debug_file", parse_with_register_value)
    getattr(setup, "__mock_auth_requests")(requests_mock)
    getattr(setup, "__mock_data_requests")(requests_mock, test_data_file)

    return Thermia("username", "password").heat_pumps[0]


@pytest.mark.parametrize(
    "test_data_file, register_name, value, expected",
    [
        ("diplomat_duo_921.txt", "COMP_STATUS", 0, []),
        ("diplomat_duo_921.txt", "COMP_STATUS", 4, ["RADIATORPUMP"]),
        # Hot water production, not cooling
        (
            "diplomat_duo_921.txt",
            "COMP_STATUS",
            19,
            ["COMPR", "BRINEPUMP", "HOT_WATER"],
        ),
        (
            "diplomat_duo_921.txt",
            "COMP_STATUS",
            39,
            ["COMPR", "BRINEPUMP", "RADIATORPUMP", "HEATING"],
        ),
        ("diplomat_duo_921.txt", "COMP_STATUS", 35, ["COMPR", "BRINEPUMP", "HEATING"]),
        ("ATEC_DHP_AQ.txt", "COMP_STATUS_ATEC", 25, ["COMPR", "HOT_WATER", "HEATING"]),
        # Bit 4 has no value name, so it is ignored rather than hiding the rest
        ("iTec_IQ.txt", "COMP_STATUS_ITEC", 21, ["COMPR", "HEATING"]),
        (
            "ncp_1024.txt",
            "REG_OPERATIONAL_STATUS_PRIORITY_BITMASK",
            264,
            ["STATUS_HEAT"],
        ),
    ],
)
def test_running_operational_statuses_are_decoded_as_bitmask(
    requests_mock, monkeypatch, test_data_file, register_name, value, expected
):
    heat_pump = load_heat_pump(
        requests_mock, monkeypatch, test_data_file, register_name, value
    )

    assert match_lists_in_any_order(
        heat_pump.running_operational_statuses, expected
    ), f"expected: {expected}, got: {heat_pump.running_operational_statuses}"


@pytest.mark.parametrize("value, expected", [(4, ["RADIATORPUMP"]), (5, [])])
def test_status_flags_presentation_is_decoded_as_single_value(
    requests_mock, monkeypatch, value, expected
):
    heat_pump = load_heat_pump(
        requests_mock,
        monkeypatch,
        "diplomat_duo_921.txt",
        "COMP_STATUS",
        value,
        presentation="StatusFlags",
    )

    assert heat_pump.running_operational_statuses == expected


@pytest.mark.parametrize("value, expected", [(0, []), (3, ["3KW", "6KW"])])
def test_running_power_statuses_are_decoded_as_bitmask(
    requests_mock, monkeypatch, value, expected
):
    heat_pump = load_heat_pump(
        requests_mock,
        monkeypatch,
        "diplomat_duo_921.txt",
        "COMP_POWER_STATUS",
        value,
    )

    assert match_lists_in_any_order(heat_pump.running_power_statuses, expected)
