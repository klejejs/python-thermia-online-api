import pytest

from ..api.ThermiaAPI import ThermiaAPI


@pytest.mark.parametrize(
    "register_name",
    ["REG_HOT_WATER_BOOST", "REG__HOT_WATER_BOOST"],
)
def test_hot_water_boost_register_name_aliases(monkeypatch, register_name):
    register_group = [
        {
            "registerId": 115521,
            "registerName": "REG_HOT_WATER_STATUS",
            "registerValue": 1.0,
            "valueNames": [{"value": 0}, {"value": 1}],
        },
        {
            "registerId": 115537,
            "registerName": register_name,
            "registerValue": 1.0,
            "valueNames": [{"value": 0}, {"value": 1}],
        },
    ]

    class HeatPump:
        id = "test-device"

        def set_register_index_hot_water_switch(self, register_index):
            self.hot_water_switch_register_index = register_index

        def set_register_index_hot_water_boost_switch(self, register_index):
            self.hot_water_boost_register_index = register_index

    api = ThermiaAPI.__new__(ThermiaAPI)
    monkeypatch.setattr(
        api,
        "_ThermiaAPI__get_register_group",
        lambda _device_id, _register_group: register_group,
    )

    heat_pump = HeatPump()
    state = api.get_group_hot_water(heat_pump)

    assert state == {"hot_water_switch": 1, "hot_water_boost_switch": 1}
    assert heat_pump.hot_water_switch_register_index == 115521
    assert heat_pump.hot_water_boost_register_index == 115537
