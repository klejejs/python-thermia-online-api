import json
import logging

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..api.ThermiaAPI import ThermiaAPI

LOGGER = logging.getLogger(__name__)

class ThermiaWaterHeater():
    def __init__(self, device_data: json, api_interface: "ThermiaAPI"):
        self.__device_data = device_data
        self.__api_interface = api_interface
        self.__info = None
        self.__status = None
        self.__operation_mode_state = None

        self.refetch_data()

    def refetch_data(self):
        self.__info = self.__api_interface.get_device_info(self.__device_data)
        self.__status = self.__api_interface.get_device_status(self.__device_data)
        self.__operation_mode_state = self.__api_interface.get_operation_mode(self.__device_data)

    def set_temperature(self, temperature: int):
        LOGGER.info("Setting temperature to " + str(temperature))
        self.__api_interface.set_temperature(self, temperature)
        self.refetch_data()

    def set_operation_mode(self, mode: str):
        LOGGER.info("Setting operation mode to " + str(mode))
        self.__api_interface.set_operation_mode(self, mode)
        self.refetch_data()

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
    def has_indoor_temp_sensor(self):
        return self.__status.get("hasIndoorTempSensor")

    @property
    def indoor_temperature(self):
        return self.__status.get("indoorTemperature")

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
    def operation_mode(self):
        return self.__operation_mode_state["current"]

    @property
    def available_operation_modes(self):
        return self.__operation_mode_state["available"]
