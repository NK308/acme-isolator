import pytest
import pytest_asyncio
from .staging_fixtures import directory_resource_json

import asyncio

from acme_isolator.acme.request.session import Session


@pytest.mark.staging
@pytest.mark.asyncio
async def test_context(staging_api_url):
    async with Session(staging_api_url) as session:
        pass


@pytest.mark.staging
@pytest.mark.asyncio
async def test_nonce(staging_api_url, aiosession, event_loop):
    asyncio.set_event_loop(event_loop)
    loop = event_loop
    session = Session(staging_api_url)
    async with session:
        assert session.directory.newNonce == directory_resource_json["newNonce"]
        assert session.resource_sessions["newNonce"] is not None
        await asyncio.sleep(5)
        assert len(session.sessions) == 1
        assert session.nonce_pool.initialized
        assert session.nonce_pool.loop is not None
        assert await session.nonce_pool.get_nonce() is not None


@pytest.mark.staging
@pytest.mark.asyncio
async def test_session_count(staging_api_url):
    async with Session(staging_api_url) as session:
        assert set(session.sessions.keys()) == {"https://acme-staging-v02.api.letsencrypt.org"}
