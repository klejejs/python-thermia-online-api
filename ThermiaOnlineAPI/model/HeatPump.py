import json
import logging

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..api.ThermiaAPI import ThermiaAPI

LOGGER = logging.getLogger(__name__)

DEFAULT_REGISTER_INDEXES = {
    "temperature": None,
    "operation_mode": None,
    "hot_water_switch": None,
}


class ThermiaHeatPump:
    def __init__(self, device_data: json, api_interface: "ThermiaAPI"):
        self.__device_id = str(device_data["id"])
        self.__api_interface = api_interface

        self.__info = None
        self.__status = None
        self.__device_data = None

        self.__temperature_state = None
        self.__operation_mode_state = None
        self.__hot_water_switch_state = None

        self.__alarms = None

        self.__register_indexes = DEFAULT_REGISTER_INDEXES

        self.update_data()

    def update_data(self):
        self.__info = self.__api_interface.get_device_info(self.__device_id)
        self.__status = self.__api_interface.get_device_status(self.__device_id)
        self.__device_data = self.__api_interface.get_device_by_id(self.__device_id)

        self.__register_indexes["temperature"] = self.__status.get(
            "heatingEffectRegisters", [None, None]
        )[1]

        self.__temperature_state = self.__api_interface.get_temperature_status(self)
        self.__operation_mode_state = self.__api_interface.get_operation_mode(self)
        self.__hot_water_switch_state = self.__api_interface.get_hot_water_switch_state(
            self
        )

        self.__alarms = self.__api_interface.get_all_alarms(self.__device_id)

    def get_register_indexes(self):
        return self.__register_indexes

    def set_register_index_operation_mode(self, register_index: int):
        self.__register_indexes["operation_mode"] = register_index

    def set_register_index_hot_water_switch(self, register_index: int):
        self.__register_indexes["hot_water_switch"] = register_index

    def set_temperature(self, temperature: int):
        LOGGER.info("Setting temperature to " + str(temperature))
        self.__status[
            "heatingEffect"
        ] = temperature  # update local state before refetching data
        self.__api_interface.set_temperature(self, temperature)
        self.update_data()

    def set_operation_mode(self, mode: str):
        LOGGER.info("Setting operation mode to " + str(mode))

        self.__operation_mode_state[
            "current"
        ] = mode  # update local state before refetching data
        self.__api_interface.set_operation_mode(self, mode)
        self.update_data()

    def set_hot_water_switch_state(self, state: int):
        LOGGER.info("Setting hot water switch to " + str(state))

        if self.__hot_water_switch_state is None:
            LOGGER.error("Hot water switch not available")
            return

        self.__hot_water_switch_state = (
            state  # update local state before refetching data
        )
        self.__api_interface.set_hot_water_switch_state(self, state)
        self.update_data()

    def __get_active_alarms(self):
        active_alarms = filter(
            lambda alarm: alarm.get("isActiveAlarm", False) is True, self.__alarms
        )
        return list(active_alarms)

    @property
    def name(self):
        return self.__info.get("name")

    @property
    def id(self):
        return self.__info.get("id")

    @property
    def is_online(self):
        return self.__info.get("isOnline")

    @property
    def last_online(self):
        return self.__info.get("lastOnline")

    @property
    def model(self):
        return self.__device_data.get("profile", {}).get("thermiaName")

    @property
    def has_indoor_temp_sensor(self):
        return self.__status.get("hasIndoorTempSensor")

    @property
    def indoor_temperature(self):
        if self.has_indoor_temp_sensor:
            return self.__status.get("indoorTemperature")
        else:
            return self.heat_temperature

    @property
    def is_outdoor_temp_sensor_functioning(self):
        return self.__status.get("isOutdoorTempSensorFunctioning")

    @property
    def outdoor_temperature(self):
        return self.__status.get("outdoorTemperature")

    @property
    def is_hot_water_active(self):
        return self.__status.get("isHotwaterActive")

    @property
    def hot_water_temperature(self):
        return self.__status.get("hotWaterTemperature")

    @property
    def heat_temperature(self):
        return self.__status.get("heatingEffect")

    @property
    def heat_min_temperature_value(self):
        if self.__temperature_state is None:
            return None
        return self.__temperature_state.get("minValue", None)

    @property
    def heat_max_temperature_value(self):
        if self.__temperature_state is None:
            return None
        return self.__temperature_state.get("maxValue", None)

    @property
    def heat_temperature_step(self):
        if self.__temperature_state is None:
            return None
        return self.__temperature_state.get("step", None)

    @property
    def operation_mode(self):
        if self.__operation_mode_state is None:
            return None
        return self.__operation_mode_state.get("current", None)

    @property
    def available_operation_modes(self):
        if self.__operation_mode_state is None:
            return None
        return list(self.__operation_mode_state.get("available", {}).values())

    @property
    def available_operation_mode_map(self):
        if self.__operation_mode_state is None:
            return None
        return self.__operation_mode_state.get("available", {})

    @property
    def is_operation_mode_read_only(self):
        if self.__operation_mode_state is None:
            return None
        return self.__operation_mode_state.get("isReadOnly", None)

    @property
    def is_hot_water_switch_available(self):
        return self.__hot_water_switch_state is not None

    @property
    def hot_water_switch_state(self):
        return self.__hot_water_switch_state

    @property
    def active_alarm_count(self):
        active_alarms = self.__get_active_alarms()
        return len(list(active_alarms))

    @property
    def active_alarms(self):
        active_alarms = self.__get_active_alarms()
        active_alarm_texts = map(lambda alarm: alarm.get("eventTitle"), active_alarms)
        return list(active_alarm_texts)
