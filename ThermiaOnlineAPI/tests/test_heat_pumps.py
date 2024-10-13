from .setup import setup_thermia_and_perform_basic_tests


def test_diplomat_duo_921(requests_mock):
    setup_thermia_and_perform_basic_tests(
        requests_mock,
        "diplomat_duo_921.txt",
        "Diplomat / Diplomat Duo",
        "DHP H/L/C 921",
        ["OFF", "AUTO", "COMPRESSOR", "AUXILIARY", "HOT_WATER"],
        ["COMPR", "BRINEPUMP", "HOT_WATER", "HEATING"],
        ["3KW", "6KW"],
    )


def test_itec_iq(requests_mock):
    setup_thermia_and_perform_basic_tests(
        requests_mock,
        "iTec_IQ.txt",
        "iTec",
        "IQ",
        ["OFF", "AUTO", "COMPRESSOR", "AUXILIARY"],
        ["COMPR", "HEATING", "DEFROST", "COOLING"],
        [],
    )
