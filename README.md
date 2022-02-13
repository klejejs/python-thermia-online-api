# Thermia Online API
### A Python API for Thermia heat pumps using https://online.thermia.se

## Confirmed Thermia profiles that API supports:
* Thermia Diplomat / Diplomat Duo
* Thermia iTec

## Confirmed Thermia models that API supports:
* Danfoss DHP-AQ 9

## Supported APIs:
* `classic`, default, online access url is https://online.thermia.se
* `genesis`, online access url is https://online-genesis.thermia.se

## How to use api:
See [example.py](https://github.com/klejejs/python-thermia-online-api/blob/main/example.py) file

## Available functions in Thermia class:
| Function | Description |
| --- | --- |
| `fetch_heat_pumps` | Fetches all heat pumps from Thermia Online API and their data |
| `update_data` | Updates all heat pump data |

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
| `desired_supply_line_temperature` | Desired supply line temperature in Celsius |
| `return_line_temperature` | Return line temperature in Celsius |
| `brine_out_temperature` | Brine out temperature in Celsius |
| `brine_in_temperature` | Brine in temperature in Celsius |
| `cooling_tank_temperature` | Cooling tank temperature in Celsius |
| `cooling_supply_line_temperature` | Cooling supply line temperature in Celsius |
| --- | --- |
| Operational status | |
| `operational_status` | Operational status of the Heat Pump |
| `available_operational_statuses` | List of available operational statuses |
| `available_operational_statuses_map` | Dictionary mapping operational status names to their values |
| --- | --- |
| Operational Times | |
| `compressor_operational_time` | Compressor operational time in hours |
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
| --- | --- |
| Hot Water data | |
| `is_operation_mode_read_only` | Boolean value indicating if the Heat Pump operation mode is read-only |
| `is_hot_water_switch_available` | Boolean value indicating if the Heat Pump has a hot water switch |
| --- | --- |
| Historical data | |
| `historical_data_registers` | List of available registers to use for historical data fetching |

## Available functions within ThermiaHeatPump class:
| Function | Description |
| --- | --- |
| `update_data` | Refetch all data from Thermia for Heat Pump |
| --- | --- |
| Change heat pump state | |
| `set_temperature` | Set the target temperature for the Heat Pump |
| `set_operation_mode` | Set the operation mode for the Heat Pump |
| `set_hot_water_switch_state` | Set the hot water switch state to 0 (off) or 1 (on) for the Heat Pump |
| --- | --- |
| Fetch historical data | |
| `get_historical_data_for_register` | Fetch historical data by using register name from `historical_data_registers` together with start_time and end_time of the data in Python datatime format. Returns list of dictionaries which contains data in format `{ "time": datetime, "value": int }` |
