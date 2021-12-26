from ThermiaOnlineAPI import Thermia

USERNAME = 'username'
PASSWORD = 'password'

thermia = Thermia(USERNAME, PASSWORD)

print("Connected: " + str(thermia.connected))

water_heater = thermia.water_heaters[0]

print("Name: " + water_heater.name)
print("Id: " + str(water_heater.id))
print("Is Online: " + str(water_heater.is_online))
print("Last Online: " + str(water_heater.last_online))
print("Has Indoor Temp Sensor: " + str(water_heater.has_indoor_temp_sensor))
print("Indoor Temperature: " + str(water_heater.indoor_temperature))
print("Is Outdoor Temp Sensor Functioning: " + str(water_heater.is_outdoor_temp_sensor_functioning))
print("Outdoor Temperature: " + str(water_heater.outdoor_temperature))
print("Is Hot Water Active: " + str(water_heater.is_hot_water_active))
print("Hot Water Temperature: " + str(water_heater.hot_water_temperature))
print("Heat Temperature: " + str(water_heater.heat_temperature))
print("Heat Min Temperature Value: " + str(water_heater.heat_min_temperature_value))
print("Heat Max Temperature Value: " + str(water_heater.heat_max_temperature_value))
print("Heat Temperature Step: " + str(water_heater.heat_temperature_step))
print("Operation Mode: " + str(water_heater.operation_mode))
print("Available Operation Modes: " + str(water_heater.available_operation_modes))

print("\n")

water_heater.set_temperature(19)
water_heater.set_operation_mode("COMPRESSOR")

print("Heat Temperature: " + str(water_heater.heat_temperature))
print("Operation Mode: " + str(water_heater.operation_mode))
print("Available Operation Modes: " + str(water_heater.available_operation_modes))
