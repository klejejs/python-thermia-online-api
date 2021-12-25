from api.ThermiaAPI import ThermiaAPI
from model.WaterHeater import ThermiaWaterHeater

class Thermia():
    def __init__(self, username, password):
        self.api_interface = ThermiaAPI(username, password)
        self.connected = self.api_interface.authenticated
        self.water_heaters = self.__get_water_heaters()

    def __get_water_heaters(self):
        devices = self.api_interface.get_devices()
        water_heaters = []

        for device in devices:
            water_heaters.append(ThermiaWaterHeater(device, self.api_interface))

        return water_heaters
