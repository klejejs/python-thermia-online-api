from collections import ChainMap
from datetime import datetime
import logging
import sys

from ThermiaOnlineAPI.model.CalendarFunction import CalendarFunction
from ThermiaOnlineAPI.model.CalendarSchedule import CalendarSchedule
from ..utils.utils import pretty_json_string_except

from typing import TYPE_CHECKING, Dict, List, Optional

from ThermiaOnlineAPI.const import (
    REG_BRINE_IN,
    REG_BRINE_OUT,
    REG_ACTUAL_POOL_TEMP,
    REG_COOL_SENSOR_SUPPLY,
    REG_COOL_SENSOR_TANK,
    REG_DESIRED_SUPPLY_LINE,
    REG_DESIRED_SUPPLY_LINE_TEMP,
    REG_DESIRED_SYS_SUPPLY_LINE_TEMP,
    REG_INTEGRAL_LSD,
    REG_OPERATIONAL_STATUS_PRIO1,
    REG_OPERATIONAL_STATUS_PRIORITY_BITMASK,
    REG_OPER_DATA_RETURN,
    REG_OPER_DATA_SUPPLY_MA_SA,
    REG_OPER_TIME_COMPRESSOR,
    REG_OPER_TIME_HEATING,
    REG_OPER_TIME_HOT_WATER,
    REG_OPER_TIME_IMM1,
    REG_OPER_TIME_IMM2,
    REG_OPER_TIME_IMM3,
    REG_PID,
    REG_RETURN_LINE,
    COMP_POWER_STATUS,
    COMP_STATUS,
    COMP_STATUS_ATEC,
    COMP_STATUS_ITEC,
    REG_SUPPLY_LINE,
    DATETIME_FORMAT,
    REG_OPER_DATA_BUFFER_TANK,
)

from ..utils.utils import get_dict_value_or_none, get_dict_value_or_default

if TYPE_CHECKING:
    from ..api.ThermiaAPI import ThermiaAPI

DEFAULT_REGISTER_INDEXES: Dict[str, Optional[int]] = {
    "temperature": None,
    "operation_mode": None,
    "hot_water_switch": None,
    "hot_water_boost_switch": None,
}


class ThermiaHeatPump:
    def __init__(self, device_data: dict, api_interface: "ThermiaAPI"):
        self.__device_id = str(device_data["id"])
        self.__api_interface = api_interface

        self._LOGGER = logging.getLogger(__name__ + "." + self.__device_id)

        self.__info = None
        self.__status = None
        self.__device_data = None

        self.__device_config: Dict[str, Optional[str]] = {
            "operational_status_register": None,
            "operational_status_valueNamePrefix": None,
            "operational_status_minRegisterValue": None,
        }

        # GROUPS
        self.__group_temperatures = None
        self.__group_operational_status = None
        self.__group_operational_time = None
        self.__group_operational_operation = None
        self.__group_operational_operation_read_only = None
        self.__group_hot_water: Dict[str, Optional[int]] = {
            "hot_water_switch": None,
            "hot_water_boost_switch": None,
        }

        self.__alarms = None
        self.__historical_data_registers_map = None

        self.__register_indexes = DEFAULT_REGISTER_INDEXES

        # Precalculated data so it does not have to be updated

        self.__operational_statuses = None
        self.__all_operational_statuses_map = None
        self.__running_operational_statuses = None

        self.__power_statuses = None
        self.__all_power_statuses_map = None
        self.__running_power_statuses = None

        self.update_data()

    def update_data(self):
        self.__info = self.__api_interface.get_device_info(self.__device_id)
        self.__status = self.__api_interface.get_device_status(self.__device_id)
        self.__device_data = self.__api_interface.get_device_by_id(self.__device_id)

        self.__register_indexes["temperature"] = get_dict_value_or_default(
            self.__status, "heatingEffectRegisters", [None, None]
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
        self.__group_operational_operation_read_only = (
            self.__api_interface.get_group_operational_operation_from_status(self)
        )
        self.__group_hot_water = self.__api_interface.get_group_hot_water(self)

        self.__alarms = self.__api_interface.get_all_alarms(self.__device_id)

        # Precalculate data (order is important)
        self.__operational_statuses = (
            self.__get_operational_statuses_from_operational_status()
        )
        self.__all_operational_statuses_map = (
            self.__get_all_operational_statuses_from_operational_status()
        )
        self.__running_operational_statuses = self.__get_running_operational_statuses()

        self.__power_statuses = self.__get_power_statuses_from_operational_status()
        self.__all_power_statuses_map = (
            self.__get_all_power_statuses_from_power_status()
        )
        self.__running_power_statuses = self.__get_running_power_statuses()

    def get_register_indexes(self):
        return self.__register_indexes

    def set_register_index_operation_mode(self, register_index: int):
        self.__register_indexes["operation_mode"] = register_index

    def set_register_index_hot_water_switch(self, register_index: Optional[int]):
        self.__register_indexes["hot_water_switch"] = register_index

    def set_register_index_hot_water_boost_switch(self, register_index: Optional[int]):
        self.__register_indexes["hot_water_boost_switch"] = register_index

    def set_temperature(self, temperature: int):
        if self.__status is None:
            self._LOGGER.error("Status not available, cannot set temperature")
            return

        self._LOGGER.info("Setting temperature to " + str(temperature))

        self.__status["heatingEffect"] = (
            temperature  # update local state before refetching data
        )
        self.__api_interface.set_temperature(self, temperature)
        self.update_data()

    def set_operation_mode(self, mode: str):
        self._LOGGER.info("Setting operation mode to " + str(mode))

        if self.__group_operational_operation is not None:
            self.__group_operational_operation["current"] = (
                mode  # update local state before refetching data
            )
        self.__api_interface.set_operation_mode(self, mode)
        self.update_data()

    def set_hot_water_switch_state(self, state: int):
        self._LOGGER.info("Setting hot water switch to " + str(state))

        if self.__group_hot_water["hot_water_switch"] is None:
            self._LOGGER.error("Hot water switch not available")
            return

        self.__group_hot_water["hot_water_switch"] = (
            state  # update local state before refetching data
        )
        self.__api_interface.set_hot_water_switch_state(self, state)
        self.update_data()

    def set_hot_water_boost_switch_state(self, state: int):
        self._LOGGER.info("Setting hot water boost switch to " + str(state))

        if self.__group_hot_water["hot_water_boost_switch"] is None:
            self._LOGGER.error("Hot water switch not available")
            return

        self.__group_hot_water["hot_water_boost_switch"] = (
            state  # update local state before refetching data
        )
        self.__api_interface.set_hot_water_boost_switch_state(self, state)
        self.update_data()

    def get_all_available_register_groups(self):
        installation_profile_id = get_dict_value_or_none(
            self.__info, "installationProfileId"
        )

        if installation_profile_id is None:
            return []

        register_groups = self.__api_interface.get_all_available_groups(
            installation_profile_id
        )

        if register_groups is None:
            return []

        return list(map(lambda x: x["name"], register_groups))

    def get_available_registers_for_group(self, register_group: str):
        registers_for_group = self.__api_interface.get_register_group_json(
            self.__device_id, register_group
        )

        if registers_for_group is None:
            return []

        return list(map(lambda x: x["registerName"], registers_for_group))

    def get_register_data_by_register_group_and_name(
        self, register_group: str, register_name: str
    ):
        register_group_data: list = self.__api_interface.get_register_group_json(
            self.__device_id, register_group
        )

        if register_group_data is None:
            self._LOGGER.error("No register group found for group: " + register_group)
            return None

        return self.__get_data_from_group_by_register_name(
            register_group_data, register_name
        )

    def set_register_data_by_register_group_and_name(
        self, register_group: str, register_name: str, value: int
    ):
        register_data = self.get_register_data_by_register_group_and_name(
            register_group, register_name
        )

        if register_data is None:
            self._LOGGER.error(
                "No register group found for group: "
                + register_group
                + " and register: "
                + register_name
            )
            return None

        self.__api_interface.set_register_value(self, register_data["id"], value)
        self.update_data()

    def __get_heat_temperature_data(self):
        device_temperature_register_index = self.get_register_indexes()["temperature"]
        if device_temperature_register_index is None:
            return None

        if self.__group_temperatures is None:
            return None

        data = [
            d
            for d in self.__group_temperatures
            if d["registerId"] == device_temperature_register_index
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
        self, register_name: str  # TEMPERATURE_REGISTERS
    ):
        if self.__group_temperatures is None:
            return None

        return self.__get_data_from_group_by_register_name(
            self.__group_temperatures, register_name
        )

    def __get_operational_time_data_by_register_name(
        self, register_name: str  # OPERATIONAL_TIME_REGISTERS
    ):
        if self.__group_operational_time is None:
            return None

        return self.__get_data_from_group_by_register_name(
            self.__group_operational_time, register_name
        )

    def __get_data_from_group_by_register_name(self, group: list, register_name: str):
        if group is None:
            return None

        data = [d for d in group if d["registerName"] == register_name]

        if len(data) != 1:
            # Register not in the group
            return None

        data = data[0]

        return {
            "id": data["registerId"],
            "isReadOnly": data["isReadOnly"],
            "minValue": data["minValue"],
            "maxValue": data["maxValue"],
            "step": data["step"],
            "value": data["registerValue"],
        }

    def __get_active_alarms(self):
        active_alarms = filter(
            lambda alarm: get_dict_value_or_default(alarm, "isActiveAlarm", False)
            is True,
            self.__alarms or [],
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

    def __get_register_from_operational_status(
        self, register_name: str
    ) -> Optional[Dict]:
        data = [
            d
            for d in self.__group_operational_status or []
            if d["registerName"] == register_name
        ]

        if len(data) != 1:
            return None

        return data[0]

    def __get_operational_statuses_from_operational_status(self) -> Optional[Dict]:
        if self.__device_config["operational_status_register"] is not None:
            data = self.__get_register_from_operational_status(
                self.__device_config["operational_status_register"]
            )
            if data is not None:
                return data.get("valueNames", [])

        # Try to get the data from the REG_OPERATIONAL_STATUS_PRIO1 register
        data = self.__get_register_from_operational_status(REG_OPERATIONAL_STATUS_PRIO1)
        if data is not None:
            self.__device_config["operational_status_register"] = (
                REG_OPERATIONAL_STATUS_PRIO1
            )
            self.__device_config["operational_status_valueNamePrefix"] = (
                "REG_VALUE_STATUS_"
            )
            return data.get("valueNames", [])

        # Try to get the data from the COMP_STATUS_ATEC register
        data = self.__get_register_from_operational_status(COMP_STATUS_ATEC)
        if data is not None:
            self.__device_config["operational_status_register"] = COMP_STATUS_ATEC
            self.__device_config["operational_status_valueNamePrefix"] = "COMP_VALUE_"
            return data.get("valueNames", [])

        # Try to get the data from the COMP_STATUS_ITEC register
        data = self.__get_register_from_operational_status(COMP_STATUS_ITEC)
        if data is not None:
            self.__device_config["operational_status_register"] = COMP_STATUS_ITEC
            self.__device_config["operational_status_valueNamePrefix"] = "COMP_VALUE_"
            return data.get("valueNames", [])

        # Try to get the data from the REG_OPERATIONAL_STATUS_PRIORITY_BITMASK register
        data = self.__get_register_from_operational_status(
            REG_OPERATIONAL_STATUS_PRIORITY_BITMASK
        )
        if data is not None:
            self.__device_config["operational_status_register"] = (
                REG_OPERATIONAL_STATUS_PRIORITY_BITMASK
            )
            self.__device_config["operational_status_valueNamePrefix"] = "REG_VALUE_"
            return data.get("valueNames", [])

        # Try to get the data from the COMP_STATUS register
        data = self.__get_register_from_operational_status(COMP_STATUS)
        if data is not None:
            self.__device_config["operational_status_register"] = COMP_STATUS
            self.__device_config["operational_status_valueNamePrefix"] = "COMP_VALUE_"
            self.__device_config["operational_status_minRegisterValue"] = (
                "4"  # 4 is OFF
            )
            return data.get("valueNames", [])

        return None

    def __get_all_operational_statuses_from_operational_status(
        self,
    ) -> Optional[ChainMap]:
        data = self.__operational_statuses

        if data is None:
            return ChainMap()

        operation_statuses_map = map(
            lambda values: {
                values.get("value"): values.get("name").split(
                    self.__device_config["operational_status_valueNamePrefix"]
                )[1],
            },
            data,
        )

        operation_statuses_list = list(operation_statuses_map)
        return ChainMap(*operation_statuses_list)

    def __get_running_operational_statuses(
        self,
    ) -> List[str]:
        if self.__device_config["operational_status_register"] is None:
            return []

        data = self.__get_register_from_operational_status(
            self.__device_config["operational_status_register"]
        )

        if data is None:
            return []

        current_register_value = get_dict_value_or_none(data, "registerValue")

        data = self.__all_operational_statuses_map

        if data is None:
            return []

        data_items_list = list(data.items())

        current_operation_mode = [
            value for key, value in data_items_list if key == current_register_value
        ]

        if len(current_operation_mode) == 1:
            return current_operation_mode

        if (
            len(current_operation_mode) != 1
            and current_register_value > 0
            and len(data_items_list) > 1
        ):
            # Attempt to get multiple statuses by binary sum of the values
            data_items_list.sort(key=lambda x: x[0], reverse=True)
            list_of_current_operation_statuses = []

            if self.__device_config["operational_status_minRegisterValue"] is not None:
                current_register_value -= int(
                    self.__device_config["operational_status_minRegisterValue"]
                )

            for key, value in data_items_list:
                if key <= current_register_value:
                    current_register_value -= key
                    list_of_current_operation_statuses.append(value)

            if current_register_value == 0:
                return list_of_current_operation_statuses

        return []

    def __get_power_statuses_from_operational_status(self) -> Optional[Dict]:
        data = self.__get_register_from_operational_status(COMP_POWER_STATUS)

        if data is None:
            return None

        return data.get("valueNames", [])

    def __get_all_power_statuses_from_power_status(
        self,
    ) -> Optional[ChainMap]:
        data = self.__power_statuses

        if data is None:
            return ChainMap()

        power_statuses_map = map(
            lambda values: {
                values.get("value"): values.get("name").split("COMP_VALUE_STEP_")[1],
            },
            data,
        )

        power_statuses_list = list(power_statuses_map)
        return ChainMap(*power_statuses_list)

    def __get_running_power_statuses(
        self,
    ) -> List[str]:
        data = self.__get_register_from_operational_status(COMP_POWER_STATUS)

        if data is None:
            return []

        current_register_value = get_dict_value_or_none(data, "registerValue")

        data = self.__all_power_statuses_map

        if data is None:
            return []

        data_items_list = list(data.items())

        current_power_status = [
            value for key, value in data_items_list if key == current_register_value
        ]

        if len(current_power_status) == 1:
            return current_power_status

        if (
            len(current_power_status) != 1
            and current_register_value > 0
            and len(data_items_list) > 1
        ):
            # Attempt to get multiple statuses by binary sum of the values
            data_items_list.sort(key=lambda x: x[0], reverse=True)
            list_of_current_power_statuses = []

            for key, value in data_items_list:
                if key <= current_register_value:
                    current_register_value -= key
                    list_of_current_power_statuses.append(value)

            if current_register_value == 0:
                return list_of_current_power_statuses

        return []

    @property
    def name(self):
        return get_dict_value_or_none(self.__info, "name")

    @property
    def id(self):
        return self.__device_id

    @property
    def is_online(self):
        return get_dict_value_or_none(self.__info, "isOnline")

    @property
    def last_online(self):
        return get_dict_value_or_none(self.__info, "lastOnline")

    @property
    def installation_timezone(self) -> str:
        return get_dict_value_or_none(self.__info, "timeZoneId")

    @property
    def model(self):
        return get_dict_value_or_default(self.__device_data, "profile", {}).get(
            "thermiaName"
        )

    @property
    def model_id(self):
        return get_dict_value_or_default(self.__device_data, "profile", {}).get("name")

    @property
    def has_indoor_temp_sensor(self):
        return get_dict_value_or_none(self.__status, "hasIndoorTempSensor")

    @property
    def indoor_temperature(self):
        if self.has_indoor_temp_sensor:
            return get_dict_value_or_none(self.__status, "indoorTemperature")
        else:
            return self.heat_temperature

    @property
    def is_outdoor_temp_sensor_functioning(self):
        return get_dict_value_or_none(self.__status, "isOutdoorTempSensorFunctioning")

    @property
    def outdoor_temperature(self):
        return get_dict_value_or_none(self.__status, "outdoorTemperature")

    @property
    def is_hot_water_active(self):
        return get_dict_value_or_none(
            self.__status, "isHotwaterActive"
        ) or get_dict_value_or_none(self.__status, "isHotWaterActive")

    @property
    def hot_water_temperature(self):
        return get_dict_value_or_none(self.__status, "hotWaterTemperature")

    ###########################################################################
    # Heat temperature data
    ###########################################################################

    @property
    def heat_temperature(self):
        return get_dict_value_or_none(self.__status, "heatingEffect")

    @property
    def heat_min_temperature_value(self):
        return get_dict_value_or_none(self.__get_heat_temperature_data(), "minValue")

    @property
    def heat_max_temperature_value(self):
        return get_dict_value_or_none(self.__get_heat_temperature_data(), "maxValue")

    @property
    def heat_temperature_step(self):
        return get_dict_value_or_none(self.__get_heat_temperature_data(), "step")

    ###########################################################################
    # Other temperature data
    ###########################################################################

    @property
    def supply_line_temperature(self):
        return get_dict_value_or_none(
            self.__get_temperature_data_by_register_name(REG_SUPPLY_LINE), "value"
        ) or get_dict_value_or_none(
            self.__get_temperature_data_by_register_name(REG_OPER_DATA_SUPPLY_MA_SA),
            "value",
        )

    @property
    def desired_supply_line_temperature(self):
        return (
            get_dict_value_or_none(
                self.__get_temperature_data_by_register_name(REG_DESIRED_SUPPLY_LINE),
                "value",
            )
            or get_dict_value_or_none(
                self.__get_temperature_data_by_register_name(
                    REG_DESIRED_SUPPLY_LINE_TEMP
                ),
                "value",
            )
            or get_dict_value_or_none(
                self.__get_temperature_data_by_register_name(
                    REG_DESIRED_SYS_SUPPLY_LINE_TEMP
                ),
                "value",
            )
        )

    @property
    def buffer_tank_temperature(self):
        return get_dict_value_or_none(
            self.__get_temperature_data_by_register_name(REG_OPER_DATA_BUFFER_TANK),
            "value",
        )

    @property
    def return_line_temperature(self):
        return get_dict_value_or_none(
            self.__get_temperature_data_by_register_name(REG_RETURN_LINE), "value"
        ) or get_dict_value_or_none(
            self.__get_temperature_data_by_register_name(REG_OPER_DATA_RETURN), "value"
        )

    @property
    def brine_out_temperature(self):
        return get_dict_value_or_none(
            self.__get_temperature_data_by_register_name(REG_BRINE_OUT), "value"
        )

    @property
    def pool_temperature(self):
        return get_dict_value_or_none(
            self.__get_temperature_data_by_register_name(REG_ACTUAL_POOL_TEMP), "value"
        )

    @property
    def brine_in_temperature(self):
        return get_dict_value_or_none(
            self.__get_temperature_data_by_register_name(REG_BRINE_IN), "value"
        )

    @property
    def cooling_tank_temperature(self):
        return get_dict_value_or_none(
            self.__get_temperature_data_by_register_name(REG_COOL_SENSOR_TANK), "value"
        )

    @property
    def cooling_supply_line_temperature(self):
        return get_dict_value_or_none(
            self.__get_temperature_data_by_register_name(REG_COOL_SENSOR_SUPPLY),
            "value",
        )

    ###########################################################################
    # Operational status (REG_GROUP_OPERATIONAL_STATUS)
    ###########################################################################

    @property
    def running_operational_statuses(self) -> List[str]:
        data = self.__running_operational_statuses

        if data is None:
            return []

        return data

    @property
    def available_operational_statuses(self) -> Optional[List[str]]:
        data = self.__all_operational_statuses_map

        if data is None:
            return []

        return list(data.values())

    @property
    def available_operational_statuses_map(self) -> Optional[ChainMap]:
        return self.__all_operational_statuses_map

    @property
    def running_power_statuses(self) -> List[str]:
        data = self.__running_power_statuses

        if data is None:
            return []

        return data

    @property
    def available_power_statuses(self) -> Optional[List[str]]:
        data = self.__all_power_statuses_map

        if data is None:
            return []

        return list(data.values())

    @property
    def available_power_statuses_map(self) -> Optional[ChainMap]:
        return self.__all_power_statuses_map

    @property
    def operational_status_integral(self):
        data = self.__get_register_from_operational_status(REG_INTEGRAL_LSD)
        return get_dict_value_or_none(data, "registerValue")

    @property
    def operational_status_pid(self) -> Optional[int]:
        data = self.__get_register_from_operational_status(REG_PID)
        return get_dict_value_or_none(data, "registerValue")

    ###########################################################################
    # Operational time data
    ###########################################################################

    @property
    def compressor_operational_time(self):
        return get_dict_value_or_none(
            self.__get_operational_time_data_by_register_name(REG_OPER_TIME_COMPRESSOR),
            "value",
        )

    @property
    def heating_operational_time(self):
        return get_dict_value_or_none(
            self.__get_operational_time_data_by_register_name(REG_OPER_TIME_HEATING),
            "value",
        )

    @property
    def hot_water_operational_time(self):
        return get_dict_value_or_none(
            self.__get_operational_time_data_by_register_name(REG_OPER_TIME_HOT_WATER),
            "value",
        )

    @property
    def auxiliary_heater_1_operational_time(self):
        return get_dict_value_or_none(
            self.__get_operational_time_data_by_register_name(REG_OPER_TIME_IMM1),
            "value",
        )

    @property
    def auxiliary_heater_2_operational_time(self):
        return get_dict_value_or_none(
            self.__get_operational_time_data_by_register_name(REG_OPER_TIME_IMM2),
            "value",
        )

    @property
    def auxiliary_heater_3_operational_time(self):
        return get_dict_value_or_none(
            self.__get_operational_time_data_by_register_name(REG_OPER_TIME_IMM3),
            "value",
        )

    ###########################################################################
    # Operation mode data
    ###########################################################################

    @property
    def operation_mode(self):
        if self.__group_operational_operation is not None:
            return get_dict_value_or_none(self.__group_operational_operation, "current")

        return get_dict_value_or_none(
            self.__group_operational_operation_read_only, "current"
        )

    @property
    def available_operation_modes(self):
        if self.__group_operational_operation is not None:
            return list(
                get_dict_value_or_default(
                    self.__group_operational_operation, "available", {}
                ).values()
            )

        return list(
            get_dict_value_or_default(
                self.__group_operational_operation_read_only, "available", {}
            ).values()
        )

    @property
    def available_operation_mode_map(self):
        if self.__group_operational_operation is not None:
            return get_dict_value_or_default(
                self.__group_operational_operation, "available", {}
            )

        return get_dict_value_or_default(
            self.__group_operational_operation_read_only, "available", {}
        )

    @property
    def is_operation_mode_read_only(self):
        if self.__group_operational_operation is not None:
            return get_dict_value_or_none(
                self.__group_operational_operation, "isReadOnly"
            )

        if self.__group_operational_operation_read_only is not None:
            return True

        return None

    ###########################################################################
    # Hot water data
    ###########################################################################

    @property
    def hot_water_switch_state(self) -> Optional[int]:
        return self.__group_hot_water["hot_water_switch"]

    @property
    def hot_water_boost_switch_state(self) -> Optional[int]:
        return self.__group_hot_water["hot_water_boost_switch"]

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

        return list((self.__historical_data_registers_map or {}).keys())

    def get_historical_data_for_register(
        self, register_name, start_date: datetime, end_date: datetime
    ):
        if self.__historical_data_registers_map is None:
            self.__set_historical_data_registers()

        register_id = get_dict_value_or_none(
            self.__historical_data_registers_map, register_name
        )

        if register_id is None:
            self._LOGGER.error("Register name is not supported: " + str(register_name))
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

    ###########################################################################
    # Schedules and Calendar functions
    ###########################################################################

    def get_supported_calendar_functions(self) -> List[str]:
        """
        Retrieve the supported calendar functions for the heat pump installation.

        This method fetches the supported calendar functions associated with the heat pump installation
        identified by the instance's ID.

        Returns:
            list: A list of supported calendar functions for the heat pump installation.
        """
        installation_id = self.id
        data = self.__api_interface.get_supported_calendar_functions(installation_id)
        functions = [CalendarFunction.fromJSON(entry) for entry in data]
        return functions

    def get_schedules(self) -> List[CalendarSchedule]:
        """
        Retrieve the schedules for the heat pump installation.

        This method fetches the schedules associated with the heat pump installation
        identified by the instance's ID.

        Returns:
            list: A list of schedules for the heat pump installation.
        """
        installation_id = self.id
        data = self.__api_interface.get_schedules(installation_id)
        schedules = [CalendarSchedule.fromJSON(entry) for entry in data]

        return schedules

    def add_new_schedule(self, schedule: CalendarSchedule) -> CalendarSchedule:
        """
        Adds a new schedule to the heat pump installation.

        Args:
            schedule (Schedule): The schedule to be added.

        Returns:
            Schedule: The newly added schedule with updated information from the API.
        """
        installation_id = self.id
        schedule.set_installationId(installation_id)

        data = self.__api_interface.add_new_schedule(installation_id, schedule.toJSON())
        return CalendarSchedule.fromJSON(data)

    def delete_schedule(self, schedule: CalendarSchedule):
        """
        deletes a given schedule from the heat pump installation.

        Args:
            schedule (Schedule): The schedule to be deleted.

        Returns:
            Schedule: The removed schedule with updated information from the API.
        """
        installation_id = self.id
        schedule.set_installationId(installation_id)

        data = self.__api_interface.delete_schedule(installation_id, schedule.id)
        return

    ###########################################################################
    # Print debug data
    ###########################################################################

    def debug(self) -> str:
        debug_str = "########## DEBUG START ##########\n"

        debug_str += "self.__info:\n"

        debug_str += pretty_json_string_except(
            self.__info,
            [
                "deviceId",
                "name",
                "address",
                "macAddress",
                "ownerId",
                "retailerAccess",
                "retailerId",
                "timeZoneId",
                "id",
                "hasUserAccount",
            ],
        )

        debug_str += "self.__status:\n"

        debug_str += pretty_json_string_except(self.__status)

        debug_str += "self.__device_data:\n"

        debug_str += pretty_json_string_except(
            self.__device_data,
            [
                "deviceId",
                "location",
                "name",
                "macAddress",
                "owner",
                "retailerAccess",
                "retailerId",
                "id",
                "status",
            ],
        )

        installation_profile_id = get_dict_value_or_none(
            self.__info, "installationProfileId"
        )

        if installation_profile_id is not None:
            all_available_groups = self.__api_interface.get_all_available_groups(
                installation_profile_id
            )
            if all_available_groups is not None:
                debug_str += "All available groups:\n"
                debug_str += pretty_json_string_except(all_available_groups)

                for group in all_available_groups:
                    group_name = group.get("name")
                    if group_name is not None:
                        debug_str += "Group " + group_name + ":\n"
                        group_data = self.__api_interface.get_register_group_json(
                            self.__device_id, group_name
                        )
                        debug_str += pretty_json_string_except(group_data)

        debug_str += "########## DEBUG END ##########\n"

        return debug_str
