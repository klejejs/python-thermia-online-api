from datetime import datetime
import json
import logging

from typing import TYPE_CHECKING

from ThermiaOnlineAPI.const import (
    OPERATIONAL_TIME_REGISTERS,
    REG_BRINE_IN,
    REG_BRINE_OUT,
    REG_COOL_SENSOR_SUPPLY,
    REG_COOL_SENSOR_TANK,
    REG_DESIRED_SUPPLY_LINE,
    REG_DESIRED_SUPPLY_LINE_TEMP,
    REG_DESIRED_SYS_SUPPLY_LINE_TEMP,
    REG_OPER_DATA_RETURN,
    REG_OPER_DATA_SUPPLY_MA_SA,
    REG_OPER_TIME_COMPRESSOR,
    REG_OPER_TIME_HOT_WATER,
    REG_OPER_TIME_IMM1,
    REG_OPER_TIME_IMM2,
    REG_OPER_TIME_IMM3,
    REG_RETURN_LINE,
    REG_SUPPLY_LINE,
    TEMPERATURE_REGISTERS,
    DATETIME_FORMAT,
)

from ..utils.utils import get_dict_value_safe

if TYPE_CHECKING:
    from ..api.ThermiaAPI import ThermiaAPI

_LOGGER = logging.getLogger(__name__)

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

        # GROUPS
        self.__group_temperatures = None
        self.__group_operational_status = None
        self.__group_operational_time = None
        self.__group_operational_operation = None
        self.__group_hot_water = None

        self.__alarms = None
        self.__historical_data_registers_map = None

        self.__register_indexes = DEFAULT_REGISTER_INDEXES

        self.update_data()

    def update_data(self):
        self.__info = self.__api_interface.get_device_info(self.__device_id)
        self.__status = self.__api_interface.get_device_status(self.__device_id)
        self.__device_data = self.__api_interface.get_device_by_id(self.__device_id)

        self.__register_indexes["temperature"] = self.__status.get(
            "heatingEffectRegisters", [None, None]
        )[1]

        self.__group_temperatures = self.__api_interface.get__group_temperatures(
            self.__device_id
        )
        self.__group_operational_status = (
            self.__api_interface.get__group_operational_status(self.__device_id)
        )
        self.__group_operational_time = (
            self.__api_interface.get__group_operational_time(self.__device_id)
        )
        self.__group_operational_operation = (
            self.__api_interface.get_group_operational_operation(self)
        )
        self.__group_hot_water = self.__api_interface.get_group_hot_water(self)

        self.__alarms = self.__api_interface.get_all_alarms(self.__device_id)

    def get_register_indexes(self):
        return self.__register_indexes

    def set_register_index_operation_mode(self, register_index: int):
        self.__register_indexes["operation_mode"] = register_index

    def set_register_index_hot_water_switch(self, register_index: int):
        self.__register_indexes["hot_water_switch"] = register_index

    def set_temperature(self, temperature: int):
        _LOGGER.info("Setting temperature to " + str(temperature))
        self.__status[
            "heatingEffect"
        ] = temperature  # update local state before refetching data
        self.__api_interface.set_temperature(self, temperature)
        self.update_data()

    def set_operation_mode(self, mode: str):
        _LOGGER.info("Setting operation mode to " + str(mode))

        self.__group_operational_operation[
            "current"
        ] = mode  # update local state before refetching data
        self.__api_interface.set_operation_mode(self, mode)
        self.update_data()

    def set_hot_water_switch_state(self, state: int):
        _LOGGER.info("Setting hot water switch to " + str(state))

        if self.__group_hot_water is None:
            _LOGGER.error("Hot water switch not available")
            return

        self.__group_hot_water = state  # update local state before refetching data
        self.__api_interface.set_hot_water_switch_state(self, state)
        self.update_data()

    def __get_heat_temperature_data(self):
        if not self.is_online:
            return None  # Device is offline

        device_temperature_register_index = self.get_register_indexes()["temperature"]
        if device_temperature_register_index is None:
            _LOGGER.error(
                "Error in getting device's temperature status. No temperature register index."
            )
            return None

        if self.__group_temperatures is None:
            return None

        data = [
            d
            for d in self.__group_temperatures
            if d["registerIndex"] == device_temperature_register_index
        ]

        if len(data) != 1:
            # Temperature status not supported
            return None

        data = data[0]

        return {
            "minValue": data["minValue"],
            "maxValue": data["maxValue"],
            "step": data["step"],
        }

    def __get_temperature_data_by_register_name(
        self, register_name: TEMPERATURE_REGISTERS
    ):
        return self.__get_data_from_group_by_register_name(
            self.__group_temperatures, register_name
        )

    def __get_operational_time_data_by_register_name(
        self, register_name: OPERATIONAL_TIME_REGISTERS
    ):
        return self.__get_data_from_group_by_register_name(
            self.__group_operational_time, register_name
        )

    def __get_data_from_group_by_register_name(self, group, register_name: str):
        if group is None:
            return None

        data = [d for d in group if d["registerName"] == register_name]

        if len(data) != 1:
            # Temperature status not supported
            return None

        data = data[0]

        return {
            "minValue": data["minValue"],
            "maxValue": data["maxValue"],
            "step": data["step"],
            "value": data["registerValue"],
        }

    def __get_active_alarms(self):
        active_alarms = filter(
            lambda alarm: alarm.get("isActiveAlarm", False) is True, self.__alarms
        )
        return list(active_alarms)

    def __set_historical_data_registers(self):
        data = self.__api_interface.get_historical_data_registers(self.__device_id)

        data_map = {}

        if data is not None and data.get("registers") is not None:
            registers = data["registers"]

            for register in registers:
                data_map[register["registerName"]] = register["registerId"]

        self.__historical_data_registers_map = data_map

    @property
    def name(self):
        return self.__info.get("name")

    @property
    def id(self):
        return self.__device_id

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
        return self.__status.get("isHotwaterActive") or self.__status.get(
            "isHotWaterActive"
        )

    @property
    def hot_water_temperature(self):
        return self.__status.get("hotWaterTemperature")

    ###########################################################################
    # Heat temperature data
    ###########################################################################

    @property
    def heat_temperature(self):
        return self.__status.get("heatingEffect")

    @property
    def heat_min_temperature_value(self):
        return get_dict_value_safe(self.__get_heat_temperature_data(), "minValue")

    @property
    def heat_max_temperature_value(self):
        return get_dict_value_safe(self.__get_heat_temperature_data(), "maxValue")

    @property
    def heat_temperature_step(self):
        return get_dict_value_safe(self.__get_heat_temperature_data(), "step")

    ###########################################################################
    # Other temperature data
    ###########################################################################

    @property
    def supply_line_temperature(self):
        return get_dict_value_safe(
            self.__get_temperature_data_by_register_name(REG_SUPPLY_LINE), "value"
        ) or get_dict_value_safe(
            self.__get_temperature_data_by_register_name(REG_OPER_DATA_SUPPLY_MA_SA),
            "value",
        )

    @property
    def desired_supply_line_temperature(self):
        return (
            get_dict_value_safe(
                self.__get_temperature_data_by_register_name(REG_DESIRED_SUPPLY_LINE),
                "value",
            )
            or get_dict_value_safe(
                self.__get_temperature_data_by_register_name(
                    REG_DESIRED_SUPPLY_LINE_TEMP
                ),
                "value",
            )
            or get_dict_value_safe(
                self.__get_temperature_data_by_register_name(
                    REG_DESIRED_SYS_SUPPLY_LINE_TEMP
                ),
                "value",
            )
        )

    @property
    def return_line_temperature(self):
        return get_dict_value_safe(
            self.__get_temperature_data_by_register_name(REG_RETURN_LINE), "value"
        ) or get_dict_value_safe(
            self.__get_temperature_data_by_register_name(REG_OPER_DATA_RETURN), "value"
        )

    @property
    def brine_out_temperature(self):
        return get_dict_value_safe(
            self.__get_temperature_data_by_register_name(REG_BRINE_OUT), "value"
        )

    @property
    def brine_in_temperature(self):
        return get_dict_value_safe(
            self.__get_temperature_data_by_register_name(REG_BRINE_IN), "value"
        )

    @property
    def cooling_tank_temperature(self):
        return get_dict_value_safe(
            self.__get_temperature_data_by_register_name(REG_COOL_SENSOR_TANK), "value"
        )

    @property
    def cooling_supply_line_temperature(self):
        return get_dict_value_safe(
            self.__get_temperature_data_by_register_name(REG_COOL_SENSOR_SUPPLY),
            "value",
        )

    ###########################################################################
    # Operational status data
    ###########################################################################

    @property
    def operational_status(self):
        return get_dict_value_safe(self.__group_operational_status, "current")

    @property
    def available_operational_statuses(self):
        return list(
            get_dict_value_safe(
                self.__group_operational_status, "available", {}
            ).values()
        )

    @property
    def available_operational_statuses_map(self):
        return get_dict_value_safe(self.__group_operational_status, "available", {})

    ###########################################################################
    # Operational time data
    ###########################################################################

    @property
    def compressor_operational_time(self):
        return get_dict_value_safe(
            self.__get_operational_time_data_by_register_name(REG_OPER_TIME_COMPRESSOR),
            "value",
        )

    @property
    def hot_water_operational_time(self):
        return get_dict_value_safe(
            self.__get_operational_time_data_by_register_name(REG_OPER_TIME_HOT_WATER),
            "value",
        )

    @property
    def auxiliary_heater_1_operational_time(self):
        return get_dict_value_safe(
            self.__get_operational_time_data_by_register_name(REG_OPER_TIME_IMM1),
            "value",
        )

    @property
    def auxiliary_heater_2_operational_time(self):
        return get_dict_value_safe(
            self.__get_operational_time_data_by_register_name(REG_OPER_TIME_IMM2),
            "value",
        )

    @property
    def auxiliary_heater_3_operational_time(self):
        return get_dict_value_safe(
            self.__get_operational_time_data_by_register_name(REG_OPER_TIME_IMM3),
            "value",
        )

    ###########################################################################
    # Operation mode data
    ###########################################################################

    @property
    def operation_mode(self):
        return get_dict_value_safe(self.__group_operational_operation, "current")

    @property
    def available_operation_modes(self):
        return list(
            get_dict_value_safe(
                self.__group_operational_operation, "available", {}
            ).values()
        )

    @property
    def available_operation_mode_map(self):
        return get_dict_value_safe(self.__group_operational_operation, "available", {})

    @property
    def is_operation_mode_read_only(self):
        return get_dict_value_safe(self.__group_operational_operation, "isReadOnly")

    ###########################################################################
    # Hot water switch data
    ###########################################################################

    @property
    def is_hot_water_switch_available(self):
        return self.__group_hot_water is not None

    @property
    def hot_water_switch_state(self):
        return self.__group_hot_water

    ###########################################################################
    # Alarm data
    ###########################################################################

    @property
    def active_alarm_count(self):
        active_alarms = self.__get_active_alarms()
        return len(list(active_alarms))

    @property
    def active_alarms(self):
        active_alarms = self.__get_active_alarms()
        active_alarm_texts = map(lambda alarm: alarm.get("eventTitle"), active_alarms)
        return list(active_alarm_texts)

    ###########################################################################
    # Historical data
    ###########################################################################

    @property
    def historical_data_registers(self):
        if self.__historical_data_registers_map is None:
            self.__set_historical_data_registers()

        return list(self.__historical_data_registers_map.keys())

    def get_historical_data_for_register(
        self, register_name, start_date: datetime, end_date: datetime
    ):
        if self.__historical_data_registers_map is None:
            self.__set_historical_data_registers()

        register_id = self.__historical_data_registers_map.get(register_name)

        if register_id is None:
            _LOGGER.error("Register name is not supported: " + str(register_name))
            return None

        historical_data = self.__api_interface.get_historical_data(
            self.__device_id,
            register_id,
            start_date.strftime(DATETIME_FORMAT),
            end_date.strftime(DATETIME_FORMAT),
        )

        if historical_data is None or historical_data.get("data") is None:
            return []

        return list(
            map(
                lambda entry: {
                    "time": datetime.strptime(
                        entry["at"].split(".")[0], DATETIME_FORMAT
                    ),
                    "value": int(entry["val"]),
                },
                historical_data["data"],
            )
        )
