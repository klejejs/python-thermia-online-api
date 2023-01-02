###############################################################################
# General configuration
###############################################################################

THERMIA_CLASSIC_API_CONFIG_URL = "https://online.thermia.se/api/configuration"
THERMIA_GENESIS_API_CONFIG_URL = "https://online-genesis.thermia.se/api/configuration"

THERMIA_INSTALLATION_PATH = "/api/v1/Registers/Installations/"

THERMIA_API_TYPE_CLASSIC = "classic"
THERMIA_API_TYPE_GENESIS = "genesis"

THERMIA_API_CONFIG_URLS_BY_API_TYPE = {
    THERMIA_API_TYPE_CLASSIC: THERMIA_CLASSIC_API_CONFIG_URL,
    THERMIA_API_TYPE_GENESIS: THERMIA_GENESIS_API_CONFIG_URL,
}

###############################################################################
# Azure AD configuration
###############################################################################

THERMIA_AZURE_AUTH_URL = "https://thermialogin.b2clogin.com/thermialogin.onmicrosoft.com/b2c_1a_signuporsigninonline"
THERMIA_AZURE_AUTH_CLIENT_ID_AND_SCOPE = "09ea4903-9e95-45fe-ae1f-e3b7d32fa385"
THERMIA_AZURE_AUTH_REDIRECT_URI = "https://online-genesis.thermia.se/login"

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
COMP_STATUS_ITEC = "COMP_STATUS_ITEC"  # Operational status for ITEC heat pumps
REG_OPERATIONAL_STATUS_PRIORITY_BITMASK = (
    "REG_OPERATIONAL_STATUS_PRIORITY_BITMASK"  # Operational status for Atlas heat pumps
)
REG_INTEGRAL_LSD = "REG_INTEGRAL_LSD"
REG_PID = "REG_PID"

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
REG_OPER_TIME_HOT_WATER = "REG_OPER_TIME_HOT_WATER"

###############################################################################
# Other
###############################################################################

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
