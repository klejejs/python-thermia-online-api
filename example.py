from datetime import datetime, timedelta
from ThermiaOnlineAPI import Thermia
from ThermiaOnlineAPI.const import CAL_FUNCTION_REDUCED_HEATING_EFFECT
from ThermiaOnlineAPI.model.Schedule import Schedule

CHANGE_HEAT_PUMP_DATA_DURING_TEST = (
    False  # Set to True if you want to change heat pump data during test
)

USERNAME = None
PASSWORD = None

with open(".env", "r") as env_file:
    for line in env_file:
        if line.startswith("USERNAME="):
            USERNAME = line.split("=")[1].strip()
        elif line.startswith("PASSWORD="):
            PASSWORD = line.split("=")[1].strip()

if not USERNAME or not PASSWORD:
    USERNAME = input("Enter username: ")
    PASSWORD = input("Enter password: ")

thermia = Thermia(USERNAME, PASSWORD)

print("Connected: " + str(thermia.connected))

heat_pump = thermia.heat_pumps[0]


print("Creating debug file")
with open("debug.txt", "w") as f:
    f.write(heat_pump.debug())

print("Debug file created")

print("\n")
print("\n")

print("Heat pump model: " + str(heat_pump.model))
print("Heat pump model id: " + str(heat_pump.model_id))

print("\n")

print(
    "All available register groups: "
    + str(heat_pump.get_all_available_register_groups())
)

print(
    "Available registers for 'REG_GROUP_HEATING_CURVE' group: "
    + str(heat_pump.get_available_registers_for_group("REG_GROUP_HEATING_CURVE"))
)

print("\n")

print("Other temperatures")
print("Supply Line Temperature: " + str(heat_pump.supply_line_temperature))
print(
    "Desired Supply Line Temperature: " + str(heat_pump.desired_supply_line_temperature)
)
print("Return Line Temperature: " + str(heat_pump.return_line_temperature))
print("Brine Out Temperature: " + str(heat_pump.brine_out_temperature))
print("Pool Temperature: " + str(heat_pump.pool_temperature))
print("Brine In Temperature: " + str(heat_pump.brine_in_temperature))
print("Cooling Tank Temperature: " + str(heat_pump.cooling_tank_temperature))
print(
    "Cooling Supply Line Temperature: " + str(heat_pump.cooling_supply_line_temperature)
)

print("\n")

print("Operational status")
print("Running operational statuses: " + str(heat_pump.running_operational_statuses))
print(
    "Available operational statuses: " + str(heat_pump.available_operational_statuses)
)
print(
    "Available operational statuses map: "
    + str(heat_pump.available_operational_statuses_map)
)

print("\n")

print("Power status")
print("Running power statuses: " + str(heat_pump.running_power_statuses))
print("Available power statuses: " + str(heat_pump.available_power_statuses))
print("Available power statuses map: " + str(heat_pump.available_power_statuses_map))

print("\n")

print("Integral: " + str(heat_pump.operational_status_integral))
print("Pid: " + str(heat_pump.operational_status_pid))

print("\n")

print("Operational Times")
print("Compressor Operational Time: " + str(heat_pump.compressor_operational_time))
print("Heating Operational Time: " + str(heat_pump.heating_operational_time))
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
print("Hot Water Switch State: " + str(heat_pump.hot_water_switch_state))
print("Hot Water Boost Switch State: " + str(heat_pump.hot_water_boost_switch_state))

print("\n")

print(
    "Available historical data registers: " + str(heat_pump.historical_data_registers)
)
print(
    "Historical data for outdoor temperature during past 24h: "
    + str(
        heat_pump.get_historical_data_for_register(
            "REG_OUTDOOR_TEMPERATURE",
            datetime.now() - timedelta(days=1),
            datetime.now(),
        )
    )
)

print("\n")

print(
    "Heating Curve Register Data: "
    + str(
        heat_pump.get_register_data_by_register_group_and_name(
            "REG_GROUP_HEATING_CURVE", "REG_HEATING_HEAT_CURVE"
        )
    )
)

print("\n")

thermia.update_data()

if CHANGE_HEAT_PUMP_DATA_DURING_TEST:
    heat_pump.set_temperature(19)

    heat_pump.set_register_data_by_register_group_and_name(
        "REG_GROUP_HEATING_CURVE", "REG_HEATING_HEAT_CURVE", 30
    )

    heat_pump.set_operation_mode("COMPRESSOR")

    if heat_pump.hot_water_switch_state:
        heat_pump.set_hot_water_switch_state(1)

    if heat_pump.hot_water_boost_switch_state:
        heat_pump.set_hot_water_boost_switch_state(1)

print("Heat Temperature: " + str(heat_pump.heat_temperature))
print("Operation Mode: " + str(heat_pump.operation_mode))
print("Available Operation Modes: " + str(heat_pump.available_operation_modes))

print("Hot Water Switch State: " + str(heat_pump.hot_water_switch_state))
print("Hot Water Boost Switch State: " + str(heat_pump.hot_water_boost_switch_state))

print("heat pump current schedules:\n")
schedules=heat_pump.get_schedules()
for schedule in schedules:
    print(schedule)
    print("\n")
if True:
    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=2)
    planned_schedule = Schedule(start=start_time, end=end_time, functionId=CAL_FUNCTION_REDUCED_HEATING_EFFECT, value=18)
    print("Planned schedule: " + str(planned_schedule))
    created_schedule = heat_pump.add_new_schedule(planned_schedule)
    print("Created schedule: " + str(created_schedule))
    ### deleting schedule again
    heat_pump.delete_schedule(created_schedule)
    print("Deleted schedule: " + str(created_schedule))

        
