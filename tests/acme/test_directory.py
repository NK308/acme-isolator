import sys

import pytest
from acme_isolator.acme.objects.directory import ACME_Directory
from .pebble_fixtures import *


@pytest.mark.asyncio
async def test_directory_fetching(pebble_process, pebble_CA_injection):
    d = await ACME_Directory.get_directory("https://localhost:14000/dir")
    assert type(d) == ACME_Directory


@pytest.mark.asyncio
async def test_directory_reading(pebble_process, pebble_CA_injection):
    d = await ACME_Directory.get_directory("https://localhost:14000/dir")
    assert type(d) == ACME_Directory
    print(d.newNonce, file=sys.stderr)
    d.newAccount
    d.newOrder
    d.revokeCert
    d.keyChange
    d.website
    assert d.parent is None
