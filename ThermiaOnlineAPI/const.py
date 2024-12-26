"""
This module contains constants used for configuring and interacting with the Thermia Online API.

Constants:
    THERMIA_CONFIG_URL (str): URL for Thermia configuration.
    THERMIA_INSTALLATION_PATH (str): Path for Thermia installations.

Azure AD Configuration:
    THERMIA_AZURE_AUTH_URL (str): URL for Azure AD authentication.
    THERMIA_AZURE_AUTH_CLIENT_ID_AND_SCOPE (str): Client ID and scope for Azure AD authentication.
    THERMIA_AZURE_AUTH_REDIRECT_URI (str): Redirect URI for Azure AD authentication.

Register Groups:
    REG_GROUP_TEMPERATURES (str): Register group for temperatures.
    REG_GROUP_OPERATIONAL_STATUS (str): Register group for operational status.
    REG_GROUP_OPERATIONAL_TIME (str): Register group for operational time.
    REG_GROUP_OPERATIONAL_OPERATION (str): Register group for operational operation.
    REG_GROUP_HOT_WATER (str): Register group for hot water.

Temperature Registers:
    REG_OUTDOOR_TEMPERATURE (str): Register for outdoor temperature (not used).
    REG_OPER_DATA_OUTDOOR_TEMP_MA_SA (str): Register for operational data outdoor temperature (not used).
    REG_INDOOR_TEMPERATURE (str): Register for indoor temperature.
    REG_SUPPLY_LINE (str): Register for supply line temperature.
    REG_HOT_WATER_TEMPERATURE (str): Register for hot water temperature.
    REG_BRINE_OUT (str): Register for brine out temperature.
    REG_BRINE_IN (str): Register for brine in temperature.
    REG_OPER_DATA_BUFFER_TANK (str): Register for operational data buffer tank temperature.

Temperature Registers ("classic" specific):
    REG_RETURN_LINE (str): Register for return line temperature.
    REG_DESIRED_SUPPLY_LINE (str): Register for desired supply line temperature.
    REG_OPER_DATA_SUPPLY_MA_SA (str): Register for operational data supply MA SA temperature.
    REG_DESIRED_SUPPLY_LINE_TEMP (str): Register for desired supply line temperature.
    REG_DESIRED_INDOOR_TEMPERATURE (str): Register for desired indoor temperature.

Temperature Registers ("genesis" specific):
    REG_OPER_DATA_RETURN (str): Register for operational data return temperature.
    REG_DESIRED_SYS_SUPPLY_LINE_TEMP (str): Register for desired system supply line temperature.
    REG_COOL_SENSOR_TANK (str): Register for cool sensor tank temperature.
    REG_COOL_SENSOR_SUPPLY (str): Register for cool sensor supply temperature.
    REG_ACTUAL_POOL_TEMP (str): Register for actual pool temperature.

Operational Operation Registers:
    REG_OPERATIONMODE (str): Register for operation mode.

Operational Status Registers:
    REG_OPERATIONAL_STATUS_PRIO1 (str): Register for operational status priority 1.
    COMP_STATUS (str): Register for compressor status (Diplomat heat pumps).
    COMP_STATUS_ATEC (str): Register for compressor status (ATEC heat pumps).
    COMP_STATUS_ITEC (str): Register for compressor status (ITEC heat pumps).
    REG_OPERATIONAL_STATUS_PRIORITY_BITMASK (str): Register for operational status priority bitmask (Atlas heat pumps).
    REG_INTEGRAL_LSD (str): Register for integral LSD.
    REG_PID (str): Register for PID.
    COMP_POWER_STATUS (str): Register for compressor power status.

Hot Water Registers:
    REG_HOT_WATER_STATUS (str): Register for hot water status.
    REG__HOT_WATER_BOOST (str): Register for hot water boost.

Operational Time Registers:
    REG_OPER_TIME_IMM1 (str): Register for operational time of auxiliary heater 1.
    REG_OPER_TIME_IMM2 (str): Register for operational time of auxiliary heater 2.
    REG_OPER_TIME_IMM3 (str): Register for operational time of auxiliary heater 3.
    REG_OPER_TIME_COMPRESSOR (str): Register for operational time of compressor.
    REG_OPER_TIME_HEATING (str): Register for operational time of heating.
    REG_OPER_TIME_HOT_WATER (str): Register for operational time of hot water.

Other:
    DATETIME_FORMAT (str): Date and time format commonly used in the API.

Calendar Functions:
    CAL_FUNCTION_REDUCED_HEATING_EFFECT (str): Calendar function for reduced heating effect.
    CAL_FUNCTION_HOT_WATER_BLOCK (str): Calendar function for hot water block.
    CAL_FUNCTION_SILENT_MODE (str): Calendar function for silent mode.
    CAL_FUNCTION_EVU_MODE (str): Calendar function for EVU mode.
"""
###############################################################################
# General configuration
###############################################################################

THERMIA_CONFIG_URL = "https://online.thermia.se/api/configuration"
THERMIA_INSTALLATION_PATH = "/api/v1/Registers/Installations/"

###############################################################################
# Azure AD configuration
###############################################################################

THERMIA_AZURE_AUTH_URL = "https://thermialogin.b2clogin.com/thermialogin.onmicrosoft.com/b2c_1a_signuporsigninonline"
THERMIA_AZURE_AUTH_CLIENT_ID_AND_SCOPE = "09ea4903-9e95-45fe-ae1f-e3b7d32fa385"
THERMIA_AZURE_AUTH_REDIRECT_URI = "https://online.thermia.se/login"

###############################################################################
# Register groups
###############################################################################

REG_GROUP_TEMPERATURES = "REG_GROUP_TEMPERATURES"
REG_GROUP_OPERATIONAL_STATUS = "REG_GROUP_OPERATIONAL_STATUS"
REG_GROUP_OPERATIONAL_TIME = "REG_GROUP_OPERATIONAL_TIME"
REG_GROUP_OPERATIONAL_OPERATION = "REG_GROUP_OPERATIONAL_OPERATION"
REG_GROUP_HOT_WATER = "REG_GROUP_HOT_WATER"

###############################################################################
# Temperature registers
###############################################################################

REG_OUTDOOR_TEMPERATURE = "REG_OUTDOOR_TEMPERATURE"  # Not used
REG_OPER_DATA_OUTDOOR_TEMP_MA_SA = "REG_OPER_DATA_OUTDOOR_TEMP_MA_SA"  # Not used
REG_INDOOR_TEMPERATURE = "REG_INDOOR_TEMPERATURE"
REG_SUPPLY_LINE = "REG_SUPPLY_LINE"
REG_HOT_WATER_TEMPERATURE = "REG_HOT_WATER_TEMPERATURE"
REG_BRINE_OUT = "REG_BRINE_OUT"
REG_BRINE_IN = "REG_BRINE_IN"
REG_OPER_DATA_BUFFER_TANK = "REG_OPER_DATA_BUFFER_TANK"

###############################################################################
# Temperature registers ("classic" specific)
###############################################################################

REG_RETURN_LINE = "REG_RETURN_LINE"
REG_DESIRED_SUPPLY_LINE = "REG_DESIRED_SUPPLY_LINE"
REG_OPER_DATA_SUPPLY_MA_SA = "REG_OPER_DATA_SUPPLY_MA_SA"
REG_DESIRED_SUPPLY_LINE_TEMP = "REG_DESIRED_SUPPLY_LINE_TEMP"
REG_DESIRED_INDOOR_TEMPERATURE = "REG_DESIRED_INDOOR_TEMPERATURE"

###############################################################################
# Temperature registers ("genesis" specific)
###############################################################################

REG_OPER_DATA_RETURN = "REG_OPER_DATA_RETURN"
REG_DESIRED_SYS_SUPPLY_LINE_TEMP = "REG_DESIRED_SYS_SUPPLY_LINE_TEMP"
REG_COOL_SENSOR_TANK = "REG_COOL_SENSOR_TANK"
REG_COOL_SENSOR_SUPPLY = "REG_COOL_SENSOR_SUPPLY"
REG_ACTUAL_POOL_TEMP = "REG_ACTUAL_POOL_TEMP"

###############################################################################
# Operational operation registers
###############################################################################

REG_OPERATIONMODE = "REG_OPERATIONMODE"

###############################################################################
# Operational status registers
###############################################################################

REG_OPERATIONAL_STATUS_PRIO1 = (
    "REG_OPERATIONAL_STATUS_PRIO1"  # Operational status for most heat pumps
)
COMP_STATUS = "COMP_STATUS"  # Operational status for Diplomat heat pumps
COMP_STATUS_ATEC = "COMP_STATUS_ATEC"  # Operational status for ATEC heat pumps
COMP_STATUS_ITEC = "COMP_STATUS_ITEC"  # Operational status for ITEC heat pumps
REG_OPERATIONAL_STATUS_PRIORITY_BITMASK = (
    "REG_OPERATIONAL_STATUS_PRIORITY_BITMASK"  # Operational status for Atlas heat pumps
)
REG_INTEGRAL_LSD = "REG_INTEGRAL_LSD"
REG_PID = "REG_PID"

COMP_POWER_STATUS = "COMP_POWER_STATUS"

###############################################################################
# Hot water registers
###############################################################################

REG_HOT_WATER_STATUS = "REG_HOT_WATER_STATUS"
REG__HOT_WATER_BOOST = "REG__HOT_WATER_BOOST"

###############################################################################
# Operational time registers
###############################################################################

REG_OPER_TIME_IMM1 = "REG_OPER_TIME_IMM1"  # Auxiliary heater 1
REG_OPER_TIME_IMM2 = "REG_OPER_TIME_IMM2"  # Auxiliary heater 2
REG_OPER_TIME_IMM3 = "REG_OPER_TIME_IMM3"  # Auxiliary heater 3
REG_OPER_TIME_COMPRESSOR = "REG_OPER_TIME_COMPRESSOR"
REG_OPER_TIME_HEATING = "REG_OPER_TIME_HEATING"
REG_OPER_TIME_HOT_WATER = "REG_OPER_TIME_HOT_WATER"

###############################################################################
# Other
###############################################################################

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

###############################################################################
# calendar functions
###############################################################################
CAL_FUNCTION_REDUCED_HEATING_EFFECT = "15001"
CAL_FUNCTION_HOT_WATER_BLOCK= "15002"
CAL_FUNCTION_SILENT_MODE = "15003"
CAL_FUNCTION_EVU_MODE = "15004"
