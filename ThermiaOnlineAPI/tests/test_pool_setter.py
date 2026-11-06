import json

from .setup import THERMIA_TEST_URL, setup_thermia


REGISTERS_URL = f"{THERMIA_TEST_URL}/api/v1/Registers/Installations/test-id/Registers"

REG_DESIRED_POOL_ID = 40755  # from ncp_1029.txt fixture


def test_set_pool_temperature_posts_correct_register(requests_mock):
    requests_mock.post(REGISTERS_URL, status_code=200)

    _, heat_pump = setup_thermia(requests_mock, "ncp_1029.txt")

    heat_pump.set_pool_temperature(28)

    pool_writes = [
        r for r in requests_mock.request_history
        if r.method == "POST" and r.url == REGISTERS_URL
    ]
    assert len(pool_writes) == 1, f"Expected 1 POST to Registers, got {len(pool_writes)}"

    body = json.loads(pool_writes[0].text)
    assert body["registerSpecificationId"] == REG_DESIRED_POOL_ID
    assert body["registerValue"] == 28


def test_set_pool_temperature_no_op_when_pool_unavailable(requests_mock):
    requests_mock.post(REGISTERS_URL, status_code=200)

    _, heat_pump = setup_thermia(requests_mock, "ncp_1024.txt")

    heat_pump.set_pool_temperature(28)

    pool_writes = [
        r for r in requests_mock.request_history
        if r.method == "POST" and r.url == REGISTERS_URL
    ]
    assert len(pool_writes) == 0, "Expected no POST when pool register is unavailable"
