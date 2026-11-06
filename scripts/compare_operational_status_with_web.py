"""Compare the library's operational status decoding with Thermia Online's.

The web app shows a status flag as running when (registerValue & flag) == flag,
for both the StatusFlagsTextInd and MultipleStatusFlags presentations, and lists
only flags with visible: true. Run fetch_thermia_web_app.py to re-check that rule.

This loads each debug file through the real library (HTTP mocked, no login),
sets the operational status register to every value its flags can form, and
prints where the library and the web app disagree. Run from the repository root:

    python scripts/compare_operational_status_with_web.py [debug_file ...]

With no arguments it uses every file in ThermiaOnlineAPI/tests/debug_files.
"""

import copy
import logging
import sys
from pathlib import Path

import requests_mock

from ThermiaOnlineAPI import Thermia
from ThermiaOnlineAPI.tests import setup as test_setup
from ThermiaOnlineAPI.tests.utils import parse_debug_file

DEBUG_FILES_DIR = Path("ThermiaOnlineAPI/tests/debug_files")
OPERATIONAL_STATUS_REGISTERS = [
    "REG_OPERATIONAL_STATUS_PRIO1",
    "COMP_STATUS_ATEC",
    "COMP_STATUS_ITEC",
    "REG_OPERATIONAL_STATUS_PRIORITY_BITMASK",
    "COMP_STATUS",
]
MAX_ROWS = 20


def find_status_register(data: dict):
    registers = data["groups"].get("REG_GROUP_OPERATIONAL_STATUS") or []
    by_name = {register["registerName"]: register for register in registers}
    for name in OPERATIONAL_STATUS_REGISTERS:  # same order the library tries
        if name in by_name:
            return by_name[name]
    return None


def flag_prefix(register_name: str) -> str:
    # The prefixes the library strips, so both sides use the same labels
    if register_name == "REG_OPERATIONAL_STATUS_PRIO1":
        return "REG_VALUE_STATUS_"
    return "REG_VALUE_" if register_name.startswith("REG_") else "COMP_VALUE_"


def flag_label(name: str, prefix: str) -> str:
    return name[len(prefix) :] if name.startswith(prefix) else name


def library_running_statuses(data: dict) -> list:
    test_setup.parse_debug_file = lambda *_args: data
    with requests_mock.Mocker() as mocker:
        getattr(test_setup, "__mock_auth_requests")(mocker)
        getattr(test_setup, "__mock_data_requests")(mocker, "unused")
        heat_pump = Thermia("username", "password").heat_pumps[0]
        return sorted(heat_pump.running_operational_statuses)


def web_running_statuses(value: int, flags: list, prefix: str) -> list:
    return sorted(
        flag_label(flag["name"], prefix)
        for flag in flags
        if (value & flag["value"]) == flag["value"]
    )


def compare(debug_file: Path) -> int:
    base = parse_debug_file(str(debug_file))
    register = find_status_register(base)
    if register is None:
        print(f"\n=== {debug_file.name}: no known operational status register")
        return 0

    flags = register["valueNames"]
    prefix = flag_prefix(register["registerName"])
    all_flags = 0
    for flag in flags:
        all_flags |= flag["value"]

    print(f"\n=== {debug_file.name}: {register['registerName']} ({register['presentation']})")
    print(
        "flags: "
        + ", ".join(
            f"{flag['value']}={flag_label(flag['name'], prefix)}"
            + ("" if flag.get("visible", True) else " (hidden in web UI)")
            for flag in flags
        )
    )

    disagreements = []
    values = range(all_flags + 1)
    for value in values:
        data = copy.deepcopy(base)
        find_status_register(data)["registerValue"] = float(value)
        library = library_running_statuses(data)
        web = web_running_statuses(value, flags, prefix)
        if library != web:
            known_flags_only = value & ~all_flags == 0 and all(
                value & bit == 0 or any(flag["value"] == bit for flag in flags)
                for bit in (1 << i for i in range(all_flags.bit_length()))
            )
            disagreements.append((value, library, web, known_flags_only))

    known = [d for d in disagreements if d[3]]
    print(
        f"values 0..{all_flags}: {len(disagreements)} disagree, "
        f"{len(known)} of them made only of defined flags"
    )
    for value, library, web, known_flags_only in disagreements[:MAX_ROWS]:
        note = "" if known_flags_only else "  (has undefined bits)"
        print(f"  {value:5d}: library {library}  web {web}{note}")
    if len(disagreements) > MAX_ROWS:
        print(f"  ... {len(disagreements) - MAX_ROWS} more")
    return len(known)


def main() -> None:
    logging.disable(logging.CRITICAL)
    paths = [Path(arg) for arg in sys.argv[1:]] or sorted(DEBUG_FILES_DIR.glob("*.txt"))
    total = sum(compare(path) for path in paths)
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
