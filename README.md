# Thermia Online API
### A Python API for Thermia heat pumps using https://online.thermia.se 

## Available properties within ThermiaWaterHeater class:
| Property | Description |
| --- | --- |
| `name` | Name of the Water Heater |
| `id` | Unique ID of the Water Heater Thermia generates |
| `is_online` | Boolean value indicating if the Water Heater is online or not |
| `last_online` | DateTime string indicating the last time the Water Heater was online |
| `has_indoor_temperature_sensor` | Boolean value indicating if the Water Heater has an indoor temperature sensor |
| `indoor_temperature` | Indoor temperature in Celsius, if `has_indoor_temperature_sensor` is False, this value is the same as `heat_temperature` |
| `is_outdoor_temp_sensor_functioning` | Boolean value indicating if the Water Heater has an outdoor temperature sensor |
| `outdoor_temperature` | Outdoor temperature in Celsius |
| `is_hot_water_active` | Boolean value indicating if the Water Heater is heating water |
| `hot_water_temperature` | Hot water temperature in Celsius |
| `heat_temperature` | Water Pump heating target temperature in Celsius |
| `heat_min_temperature_value` | Minimum temperature value possible for Water Heater to set |
| `heat_max_temperature_value` | Maximum temperature value possible for Water Heater to set |
| `heat_temperature_step` | Step value for temperature setting |
| `operation_mode` | Current operation mode of the Water Heater |
| `available_operation_modes` | List of available operation modes for the Water Heater |

## Available functions within ThermiaWaterHeater class:
| Function | Description |
| --- | --- |
| `refetch_data` | Refetch all data from Thermia for Water Heater |
| `set_temperature` | Set the target temperature for the Water Heater |
| `set_operation_mode` | Set the operation mode for the Water Heater |