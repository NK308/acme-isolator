import pytest
import pytest_asyncio
from .staging_fixtures import directory_resource_json

import asyncio

from acme_isolator.acme.request.session import Session


@pytest.mark.asyncio
async def test_context(pebble_api_url, pebble_CA_injection, pebble_process):
    async with Session(pebble_api_url) as session:
        pass


@pytest.mark.asyncio
async def test_nonce(aiosession, event_loop, pebble_api_url, pebble_directory):
    asyncio.set_event_loop(event_loop)
    loop = event_loop
    session = Session(pebble_api_url)
    async with session:
        assert session.directory.newNonce == pebble_directory.newNonce
        assert session.resource_sessions["newNonce"] is not None
        await asyncio.sleep(5)
        assert len(session.sessions) == 1
        assert session.nonce_pool.initialized
        assert session.nonce_pool.loop is not None
        assert await session.nonce_pool.get_nonce() is not None


@pytest.mark.asyncio
async def test_session_count(event_loop, pebble_CA_injection, pebble_api_url, pebble_process):
    asyncio.set_event_loop(event_loop)
    loop = event_loop
    async with Session(pebble_api_url) as session:
        assert len(set(session.sessions.keys())) == 1
