"""Basic tests of the Misty VM


SCL <scott@rerobots.net>
Copyright (c) 2020 rerobots, Inc.
"""
import pytest

import mistygrind


@pytest.fixture
def client(loop, aiohttp_client):
    yield loop.run_until_complete(
        aiohttp_client(mistygrind.vm.create_vm())
    )


async def test_api_battery(client):
    resp = await client.get('/api/battery')
    assert resp.status == 200
    payload = await resp.json()
    assert payload['status'] == 'Success'
    assert 'chargePercent' in payload['result'] and 'isCharging' in payload['result']
