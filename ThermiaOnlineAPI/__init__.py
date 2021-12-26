from ThermiaOnlineAPI.api.ThermiaAPI import ThermiaAPI
from ThermiaOnlineAPI.model.HeatPump import ThermiaHeatPump

class Thermia():
    def __init__(self, username, password):
        self.api_interface = ThermiaAPI(username, password)
        self.connected = self.api_interface.authenticated
        self.heat_pumps = self.__get_heat_pumps()

    def __get_heat_pumps(self):
        devices = self.api_interface.get_devices()
        heat_pumps = []

        for device in devices:
            heat_pumps.append(ThermiaHeatPump(device, self.api_interface))

        return heat_pumps
