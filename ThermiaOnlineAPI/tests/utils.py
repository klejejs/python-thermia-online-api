from typing import Any, Dict
import json


def parse_debug_file(file_path: str) -> Dict[str, Any]:
    with open(file_path, "r") as file:
        data = file.read()

    # Remove debug comments
    data = data.split("\n")
    data = [line for line in data if not line.startswith("#")]

    out_data = {
        "info": [],
        "status": [],
        "device_data": [],
        "groups": {},
    }

    parsing_key = None
    parsing_key_group = None
    empty_line_count = 0

    for line in data:
        # end of useful data
        if not line:
            empty_line_count += 1
            if empty_line_count > 1:
                # Data collection is done, it can be parsed
                if parsing_key is not None:
                    useful_data = (
                        out_data["groups"][parsing_key_group]
                        if parsing_key == "groups"
                        else out_data[parsing_key]
                    )

                    useful_data = "".join(useful_data)

                    if parsing_key == "groups":
                        out_data["groups"][parsing_key_group] = json.loads(useful_data)
                    else:
                        out_data[parsing_key] = json.loads(useful_data)

                parsing_key = None
                parsing_key_group = None
                empty_line_count = 0

            continue

        # start of new data
        if not parsing_key:
            if line.startswith("self.__info"):
                parsing_key = "info"
            elif line.startswith("self.__status:"):
                parsing_key = "status"
            elif line.startswith("self.__device_data:"):
                parsing_key = "device_data"
            elif line.startswith("Group "):
                group_id = line.split(" ")[1][:-1]  # remove colon
                out_data["groups"][group_id] = []
                parsing_key = "groups"
                parsing_key_group = group_id

            continue

        # append data to correct key
        if parsing_key == "groups":
            out_data["groups"][parsing_key_group].append(line)
        else:
            out_data[parsing_key].append(line)

    return out_data


def match_lists_in_any_order(list1, list2):
    return sorted(list1) == sorted(list2)
