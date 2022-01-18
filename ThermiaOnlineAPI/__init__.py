from ThermiaOnlineAPI.api.ThermiaAPI import ThermiaAPI
from ThermiaOnlineAPI.exceptions import AuthenticationException, NetworkException
from ThermiaOnlineAPI.model.HeatPump import ThermiaHeatPump


class Thermia:
    def __init__(self, username, password, api_type="classic"):
        self._username = username
        self._password = password

        self.api_interface = ThermiaAPI(username, password, api_type)
        self.connected = self.api_interface.authenticated

        self.heat_pumps = self.fetch_heat_pumps()

    def fetch_heat_pumps(self) -> list[ThermiaHeatPump]:
        devices = self.api_interface.get_devices()
        heat_pumps = []

        for device in devices:
            heat_pumps.append(ThermiaHeatPump(device, self.api_interface))

        return heat_pumps

    def update_data(self) -> None:
        for heat_pump in self.heat_pumps:
            heat_pump.update_data()
