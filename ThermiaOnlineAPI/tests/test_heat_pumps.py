from .setup import setup_thermia_and_perform_basic_tests


def test_diplomat_duo_921(requests_mock):
    setup_thermia_and_perform_basic_tests(
        requests_mock,
        "diplomat_duo_921.txt",
        expected_model="Diplomat / Diplomat Duo",
        expected_model_id="DHP H/L/C 921",
        expected_available_operational_modes=[
            "OFF",
            "AUTO",
            "COMPRESSOR",
            "AUXILIARY",
            "HOT_WATER",
        ],
        expected_available_operational_statuses=[
            "COMPR",
            "BRINEPUMP",
            "HOT_WATER",
            "HEATING",
        ],
        expected_available_power_statuses=["3KW", "6KW"],
    )


def test_itec_iq(requests_mock):
    setup_thermia_and_perform_basic_tests(
        requests_mock,
        "iTec_IQ.txt",
        expected_model="iTec",
        expected_model_id="IQ",
        expected_available_operational_modes=["OFF", "AUTO", "COMPRESSOR", "AUXILIARY"],
        expected_available_operational_statuses=[
            "COMPR",
            "HEATING",
            "DEFROST",
            "COOLING",
        ],
        expected_available_power_statuses=[],
    )


def test_ncp_1024(requests_mock):
    setup_thermia_and_perform_basic_tests(
        requests_mock,
        "ncp_1024.txt",
        expected_model="NCP 1024",
        expected_model_id="NCP 1024",
        expected_available_operational_modes=["OFF", "AUX_HEATER_ONLY", "AUTO"],
        expected_is_operation_mode_read_only=True,
        expected_available_operational_statuses=[
            "STATUS_MANUAL",
            "STATUS_HOTWATER",
            "STATUS_HEAT",
            "STATUS_COOL",
            "STATUS_POOL",
            "STATUS_LEGIONELLA",
            "STATUS_PASSIVE_COOL",
            "STATUS_STANDBY",
            "STATUS_NO_DEMAND",
            "OPERATION_MODE_OFF",
        ],
        expected_available_power_statuses=[],
    )


def test_ncp_1028(requests_mock):
    setup_thermia_and_perform_basic_tests(
        requests_mock,
        "ncp_1028.txt",
        expected_model="NCP 1028",
        expected_model_id="NCP 1028",
        expected_available_operational_modes=["OFF", "AUX_HEATER_ONLY", "AUTO"],
        expected_is_operation_mode_read_only=True,
        expected_available_operational_statuses=[
            "STATUS_MANUAL",
            "STATUS_HOTWATER",
            "STATUS_HEAT",
            "STATUS_COOL",
            "STATUS_POOL",
            "STATUS_LEGIONELLA",
            "STATUS_PASSIVE_COOL",
            "STATUS_STANDBY",
            "STATUS_NO_DEMAND",
            "OPERATION_MODE_OFF",
        ],
        expected_available_power_statuses=[],
    )
