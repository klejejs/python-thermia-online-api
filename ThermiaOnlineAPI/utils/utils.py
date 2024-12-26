import json
from base64 import urlsafe_b64encode
import logging
import random
import string
from typing import Any, TypeVar
import pytz
from datetime import datetime

from ThermiaOnlineAPI.utils.windows_to_pytz import WINDOWS_TO_PYTZ_MAPPING

T = TypeVar("T")


_LOGGER = logging.getLogger(__name__)


def get_pytz_timezone(windows_tz_name):
    """
    Get the corresponding pytz time zone for a given Windows time zone name.

    Args:
        windows_tz_name (str): The Windows time zone name.

    Returns:
        str: The corresponding pytz time zone name.
    """
    return WINDOWS_TO_PYTZ.get(windows_tz_name)


def adjust_times_for_timezone(timestamp: datetime, time_zone_name: str) -> datetime:

    pytz_tz_name = get_pytz_timezone(time_zone_name)
    if pytz_tz_name:
        heatpump_timezone = pytz.timezone(pytz_tz_name)
        timestamp = timestamp.astimezone(heatpump_timezone)
        return timestamp
    else:
        raise ValueError(
            f"No corresponding pytz time zone found for '{time_zone_name}'"
        )


def get_dict_value_or_none(dictionary, key) -> Any:
    if dictionary is None or key not in dictionary:
        return None
    return dictionary[key]


def get_dict_value_or_default(dictionary, key, default: T) -> T:
    if dictionary is None or key not in dictionary:
        return default
    return dictionary[key]


def get_list_value_or_default(list, idx, default: T) -> T:
    try:
        return list[idx]
    except IndexError:
        return default


def pretty_json_string(json_object) -> str:
    pretty_str = json.dumps(json_object, indent=4, sort_keys=True)
    pretty_str += "\n\n"

    return pretty_str


def pretty_json_string_except(json_object, except_keys=[]) -> str:
    if json_object is None:
        return

    json_object_copy = json_object.copy()
    for key in except_keys:
        if key in json_object_copy:
            del json_object_copy[key]

    pretty_json_str = pretty_json_string(json_object_copy)
    pretty_json_str += "\n"

    return pretty_json_str


def base64_url_encode(data):
    return urlsafe_b64encode(data).rstrip(b"=")


def generate_challenge(length):
    characters = string.ascii_letters + string.digits
    challenge = "".join(random.choice(characters) for _ in range(length))
    return challenge


def get_success_response_json_or_log_and_raise_exception(response, message: str):
    """
    Processes an HTTP response and returns its JSON content if the status code indicates success.
    Logs an error and raises an exception if the status code indicates failure or if JSON parsing fails.

    Args:
        response (requests.Response): The HTTP response object to process.
        message (str): A custom message to include in the log and exception.

    Returns:
        dict: The JSON content of the response if the status code indicates success.

    Raises:
        Exception: If the status code indicates failure or if JSON parsing fails.
    """
    if response.status_code > 100 and response.status_code < 300:
        try:
            return response.json()
        except Exception as e:
            _LOGGER.error(f"{message} {response.status_code} {response.text}")
            raise Exception(f"{message} {response.status_code} {response.text}") from e
    else:
        _LOGGER.error(f"{message} {response.status_code} {response.text}")
        raise Exception(f"{message} {response.status_code} {response.text}")


def get_response_json_or_log_and_raise_exception(response, message: str):
    try:
        return response.json()
    except Exception as e:
        _LOGGER.error(f"{message} {response.status_code} {response.text}")
        raise Exception(f"{message} {response.status_code} {response.text}") from e
