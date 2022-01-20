from ThermiaOnlineAPI import Thermia

USERNAME = "demo"
PASSWORD = "demo"

thermia = Thermia(USERNAME, PASSWORD, "classic")

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

print("\n")

print("Other temperatures")
print("Supply Line Temperature: " + str(heat_pump.supply_line_temperature))
print(
    "Desired Supply Line Temperature: " + str(heat_pump.desired_supply_line_temperature)
)
print("Return Line Temperature: " + str(heat_pump.return_line_temperature))
print("Brine Out Temperature: " + str(heat_pump.brine_out_temperature))
print("Brine In Temperature: " + str(heat_pump.brine_in_temperature))
print("Cooling Tank Temperature: " + str(heat_pump.cooling_tank_temperature))
print(
    "Cooling Supply Line Temperature: " + str(heat_pump.cooling_supply_line_temperature)
)

print("\n")

print("Operational Times")
print("Compressor Operational Time: " + str(heat_pump.compressor_operational_time))
print("Hot Water Operational Time: " + str(heat_pump.hot_water_operational_time))
print(
    "Auxiliary Heater 1 Operational Time: "
    + str(heat_pump.auxiliary_heater_1_operational_time)
)
print(
    "Auxiliary Heater 2 Operational Time: "
    + str(heat_pump.auxiliary_heater_2_operational_time)
)
print(
    "Auxiliary Heater 3 Operational Time: "
    + str(heat_pump.auxiliary_heater_3_operational_time)
)

print("\n")

print("Alarms data")
print("Active Alarm Count: " + str(heat_pump.active_alarm_count))
if heat_pump.active_alarm_count > 0:
    print("Active Alarms: " + str(heat_pump.active_alarms))

print("\n")

print("Operation Mode data")
print("Operation Mode: " + str(heat_pump.operation_mode))
print("Available Operation Modes: " + str(heat_pump.available_operation_modes))
print("Available Operation Modes Map: " + str(heat_pump.available_operation_mode_map))
print("Is Operation Mode Read Only: " + str(heat_pump.is_operation_mode_read_only))

print("\n")

print("Hot Water data")
print("Is Hot Water Switch Available: " + str(heat_pump.is_hot_water_switch_available))
if heat_pump.is_hot_water_switch_available:
    print("Hot Water Switch State: " + str(heat_pump.hot_water_switch_state))

print("\n")

thermia.update_data()

heat_pump.set_temperature(19)
heat_pump.set_operation_mode("COMPRESSOR")
if heat_pump.is_hot_water_switch_available:
    heat_pump.set_hot_water_switch_state(1)

print("Heat Temperature: " + str(heat_pump.heat_temperature))
print("Operation Mode: " + str(heat_pump.operation_mode))
print("Available Operation Modes: " + str(heat_pump.available_operation_modes))
if heat_pump.is_hot_water_switch_available:
    print("Hot Water Switch State: " + str(heat_pump.hot_water_switch_state))
