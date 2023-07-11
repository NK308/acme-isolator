import pytest
from aiohttp import ClientSession

from acme_isolator.acme.request.nonce import NonceManager
import asyncio


@pytest.mark.staging
@pytest.mark.asyncio
async def test_nonce_constructor(session, staging_directory):
    url = staging_directory["newNonce"]
    nonceManager = NonceManager(url=url, session=session)


@pytest.mark.staging
@pytest.mark.asyncio
async def test_nonce_fetch(session, staging_directory, event_loop):
    asyncio.set_event_loop(event_loop)
    url = staging_directory["newNonce"]
    nonceManager = NonceManager(url=url, session=session)
    task = asyncio.create_task(nonceManager._fetch_nonce())
    nonceManager.tasks.add(task)
    asyncio.get_running_loop()
    await asyncio.wait([task])


@pytest.mark.staging
@pytest.mark.asyncio
async def test_nonce_request(session, staging_directory, event_loop):
    asyncio.set_event_loop(event_loop)
    url = staging_directory["newNonce"]
    nonceManager = NonceManager(url=url, session=session)
    await nonceManager._request_nonce()
    task = nonceManager.tasks.__iter__().__next__()
    await asyncio.wait([task])
    nonceManager.initialized = True
    assert await nonceManager.get_nonce() is not None


@pytest.mark.staging
@pytest.mark.asyncio
async def test_nonce_context(session, staging_directory, event_loop):
    asyncio.set_event_loop(event_loop)
    url = staging_directory["newNonce"]
    nonceManager = NonceManager(url=url, session=session)
    async with nonceManager:
        assert nonceManager.initialized
        await asyncio.sleep(5)
        assert nonceManager.queue.qsize() == 10
        assert await nonceManager.get_nonce() != ""
        assert nonceManager.queue.qsize() == 9
    assert not nonceManager.initialized


@pytest.mark.staging
@pytest.mark.asyncio
async def test_nonce_exhaustion(session, staging_directory, event_loop):
    asyncio.set_event_loop(event_loop)
    url = staging_directory["newNonce"]
    nonceManager = NonceManager(url=url, session=session)
    async with nonceManager:
        for _ in range(11):
            await nonceManager.get_nonce()
