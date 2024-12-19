import os
from ThermiaOnlineAPI import Thermia

TEST_EXCLUDED_LINE_STRINGS = [
    # self.__info related
    "lastOnline",
    "activeAlarms",
    "activeCriticalAlarms",
    "unreadErrors",
    "unreadInfo",
    "unreadWarnings",
    # self.__status related
    "dcmVersion",
    "heatingEffect",
    "hotWaterTemperature",
    "indoorTemperature",
    "isHotWaterActive",
    "isOutdoorTempSensorFunctioning",
    "outdoorTemperature",
    "programVersion",
    "reducedHeatingEffect",
    # self.__device_data related
    "lastOnline",
]

REPEATING_TEST_EXCLUDED_LINE_STRINGS = [
    # Register group related
    "registerValue",
    "timeStamp",
    "value",
]


def test_excluded_string_in_lines(line1: str, line2) -> bool:
    if (
        len(TEST_EXCLUDED_LINE_STRINGS) != 0
        and TEST_EXCLUDED_LINE_STRINGS[0] in line1
        and TEST_EXCLUDED_LINE_STRINGS[0] in line2
    ):
        del TEST_EXCLUDED_LINE_STRINGS[0]
        return True

    for excluded_string in REPEATING_TEST_EXCLUDED_LINE_STRINGS:
        if excluded_string in line1 and excluded_string in line2:
            return True

    return False


USERNAME = None
PASSWORD = None

with open(".env", "r") as env_file:
    for line in env_file:
        if line.startswith("USERNAME="):
            USERNAME = line.split("=")[1].strip()
        elif line.startswith("PASSWORD="):
            PASSWORD = line.split("=")[1].strip()

if not USERNAME or not PASSWORD:
    print("Username and password not present in .env file")
    exit(1)

thermia = Thermia(USERNAME, PASSWORD)

print("Connected: " + str(thermia.connected))

heat_pump = thermia.heat_pumps[0]

print("Fetching debug data")

debug_data = heat_pump.debug()

print("Comparing debug data to existing debug file")

absolute_path = os.path.dirname(os.path.abspath(__file__))
existing_data_filename = (
    f"{absolute_path}/../ThermiaOnlineAPI/tests/debug_files/diplomat_duo_921.txt"
)

with open(existing_data_filename, "r") as f:
    existing_debug_data = f.read()

for [idx, [existing_line, new_line]] in enumerate(
    zip(existing_debug_data.split("\n"), debug_data.split("\n"))
):
    if test_excluded_string_in_lines(existing_line, new_line):
        continue

    if existing_line != new_line:
        print("Existing data does not match new data on line " + str(idx + 1))
        exit(1)

print("Debug data matches existing debug file")
