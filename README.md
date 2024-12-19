# Thermia Online API
### A Python API for Thermia heat pumps using https://online.thermia.se

## Confirmed Thermia models that API supports:
It is hard for me to keep track of all models that I have added feature support for in the past, so, to understand if your model is supported, please try running the example file and see if it works. If it does not, please submit a bug report.

### Regarding unsupported models
I am willing to do my best to support them, but as there turns out to be many different Thermia models and configurations, it is hard for me to implement all functionalities and test them thoroughly.
Thus, I have created a `debug()` function that runs when `example.py` is executed and creates a `debug.txt` file which has data about your heat pump and all its supported features. If you want to submit a bug or feature request, please include the debug file as it will make my development much easier.

## How to use api:
See [example.py](https://github.com/klejejs/python-thermia-online-api/blob/main/example.py) file for examples.

To execute the example file, first run `pip install -r requirements.txt` to install the required dependencies, then run `python3 example.py` to execute the example file. You will be prompted to enter your username and password, and then the example file will run. If do not want to manually enter your credentials every time, you can make a copy of `.env.example`, save it as a `.env` file, and add your credentials there.

## Available functions in Thermia class:
| Function | Description |
| --- | --- |
| `fetch_heat_pumps()` | Fetches all heat pumps from Thermia Online API and their data |
| `update_data()` | Updates all heat pump data |

## Available properties within ThermiaHeatPump class:
| Property | Description |
| --- | --- |
| `name` | Name of the Heat Pump |
| `id` | Unique ID of the Heat Pump Thermia generates |
| `is_online` | Boolean value indicating if the Heat Pump is online or not |
| `model` | Model of the Heat Pump |
| `last_online` | DateTime string indicating the last time the Heat Pump was online |
| `has_indoor_temperature_sensor` | Boolean value indicating if the Heat Pump has an indoor temperature sensor |
| `indoor_temperature` | Indoor temperature in Celsius, if `has_indoor_temperature_sensor` is False, this value is the same as `heat_temperature` |
| `is_outdoor_temp_sensor_functioning` | Boolean value indicating if the Heat Pump has an outdoor temperature sensor |
| `outdoor_temperature` | Outdoor temperature in Celsius |
| `is_hot_water_active` | Boolean value indicating if the Heat Pump is heating water |
| `hot_water_temperature` | Hot water temperature in Celsius |
| `heat_temperature` | Heat Pump heating target temperature in Celsius |
| `heat_min_temperature_value` | Minimum temperature value possible for Heat Pump to set |
| `heat_max_temperature_value` | Maximum temperature value possible for Heat Pump to set |
| `heat_temperature_step` | Step value for temperature setting |
| --- | --- |
| Other temperatures | |
| `supply_line_temperature` | Supply line temperature in Celsius |
| `buffer_tank_temperature` | Buffer tank temperature in Celsius |
| `desired_supply_line_temperature` | Desired supply line temperature in Celsius |
| `return_line_temperature` | Return line temperature in Celsius |
| `brine_out_temperature` | Brine out temperature in Celsius |
| `brine_in_temperature` | Brine in temperature in Celsius |
| `cooling_tank_temperature` | Cooling tank temperature in Celsius |
| `cooling_supply_line_temperature` | Cooling supply line temperature in Celsius |
| --- | --- |
| Operational status | |
| `running_operational_statuses` | List of running operational statuses of the Heat Pump  |
| `available_operational_statuses` | List of available operational statuses |
| `available_operational_statuses_map` | Dictionary mapping operational status names to their values |
| `running_power_statuses` | List of running power statuses of the Heat Pump |
| `available_power_statuses` | List of available power statuses |
| `available_power_statuses_map` | Dictionary mapping power status names to their values |
| `operational_status_integral` | Integral |
| `operational_status_pid` | PID |
| --- | --- |
| Operational Times | |
| `compressor_operational_time` | Compressor operational time in hours |
| `heating_operation_time` | Heating operational time in hours |
| `hot_water_operational_time` | Hot water operational time in hours |
| `auxiliary_heater_1_operational_time` | Auxiliary heater 1 operational time in hours |
| `auxiliary_heater_2_operational_time` | Auxiliary heater 2 operational time in hours |
| `auxiliary_heater_3_operational_time` | Auxiliary heater 3 operational time in hours |
| --- | --- |
| Alarms data | |
| `active_alarm_count` | Number of active alarms on the Heat Pump |
| `active_alarms` | List of titles of active alarms on the Heat Pump |
| --- | --- |
| Operation Mode data | |
| `operation_mode` | Current operation mode of the Heat Pump |
| `available_operation_modes` | List of available operation modes for the Heat Pump |
| `available_operation_mode_map` | Dictionary mapping operation mode names to their values |
| `is_operation_mode_read_only` | Boolean value indicating if the Heat Pump operation mode is read-only |
| --- | --- |
| Hot Water data | |
| `hot_water_switch_state` | Int value indicating the Heat Pump hot water switch state (0 or 1) or None if not available |
| `hot_water_boost_switch_state` | Int value indicating the Heat Pump hot water boost switch state (0 or 1) or None if not available |
| --- | --- |
| Historical data | |
| `historical_data_registers` | List of available registers to use for historical data fetching |

## Available functions within ThermiaHeatPump class:
| Function | Description |
| --- | --- |
| `update_data()` | Refetch all data from Thermia for Heat Pump |
| --- | --- |
| `get_all_available_register_groups()` | Return a list of all available register groups for the heat pump |
| `get_available_registers_for_group(register_group)` | Return a list of all available registers for specified register group |
| `get_register_data_by_register_group_and_name(register_group, register_name)` | Return data for specified register group and name |
| `set_register_data_by_register_group_and_name(register_group, register_name, value)` | Set register value for specified register group and name |
| --- | --- |
| Change heat pump state | |
| `set_temperature()` | Set the target temperature for the Heat Pump |
| `set_operation_mode()` | Set the operation mode for the Heat Pump |
| `set_hot_water_switch_state()` | Set the hot water switch state to 0 (off) or 1 (on) for the Heat Pump |
| `set_hot_water_boost_switch_state()` | Set the hot water boost switch state to 0 (off) or 1 (on) for the Heat Pump |
| --- | --- |
| Fetch historical data | |
| `get_historical_data_for_register()` | Fetch historical data by using register name from `historical_data_registers` together with start_time and end_time of the data in Python datatime format. Returns list of dictionaries which contains data in format `{ "time": datetime, "value": int }` |
| --- | --- |
| Fetch debug data | |
| `debug()` | Fetch debug data from Thermia API and save it to `debug.txt` file |
