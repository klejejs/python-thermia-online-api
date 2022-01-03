from ThermiaOnlineAPI import Thermia

USERNAME = 'username'
PASSWORD = 'password'

thermia = Thermia(USERNAME, PASSWORD)

print("Connected: " + str(thermia.connected))

heat_pump = thermia.fetch_heat_pumps()[0]

print("Name: " + heat_pump.name)
print("Id: " + str(heat_pump.id))
print("Is Online: " + str(heat_pump.is_online))
print("Last Online: " + str(heat_pump.last_online))
print("Model: " + str(heat_pump.model))
print("Has Indoor Temp Sensor: " + str(heat_pump.has_indoor_temp_sensor))
print("Indoor Temperature: " + str(heat_pump.indoor_temperature))
print(
    "Is Outdoor Temp Sensor Functioning: "
    + str(heat_pump.is_outdoor_temp_sensor_functioning)
)
print("Outdoor Temperature: " + str(heat_pump.outdoor_temperature))
print("Is Hot Water Active: " + str(heat_pump.is_hot_water_active))
print("Hot Water Temperature: " + str(heat_pump.hot_water_temperature))
print("Heat Temperature: " + str(heat_pump.heat_temperature))
print("Heat Min Temperature Value: " + str(heat_pump.heat_min_temperature_value))
print("Heat Max Temperature Value: " + str(heat_pump.heat_max_temperature_value))
print("Heat Temperature Step: " + str(heat_pump.heat_temperature_step))
print("Operation Mode: " + str(heat_pump.operation_mode))
print("Available Operation Modes: " + str(heat_pump.available_operation_modes))

print("\n")

thermia.update_data()

heat_pump.set_temperature(19)
heat_pump.set_operation_mode("COMPRESSOR")

print("Heat Temperature: " + str(heat_pump.heat_temperature))
print("Operation Mode: " + str(heat_pump.operation_mode))
print("Available Operation Modes: " + str(heat_pump.available_operation_modes))
