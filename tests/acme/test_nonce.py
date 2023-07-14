import pytest
from aiohttp import ClientSession

from acme_isolator.acme.request.nonce import NonceManager
import asyncio


@pytest.mark.staging
@pytest.mark.asyncio
async def test_nonce_constructor(aiosession, staging_directory):
    url = staging_directory["newNonce"]
    nonceManager = NonceManager(url=url, session=aiosession)


@pytest.mark.staging
@pytest.mark.asyncio
async def test_nonce_fetch(aiosession, staging_directory, event_loop):
    asyncio.set_event_loop(event_loop)
    url = staging_directory["newNonce"]
    nonceManager = NonceManager(url=url, session=aiosession)
    task = asyncio.create_task(nonceManager._fetch_nonce())
    nonceManager.tasks.add(task)
    asyncio.get_running_loop()
    await asyncio.wait([task])


@pytest.mark.staging
@pytest.mark.asyncio
async def test_nonce_request(aiosession, staging_directory, event_loop):
    asyncio.set_event_loop(event_loop)
    url = staging_directory["newNonce"]
    nonceManager = NonceManager(url=url, session=aiosession)
    await nonceManager._request_nonce()
    task = nonceManager.tasks.__iter__().__next__()
    await asyncio.wait([task])
    nonceManager.initialized = True
    assert await nonceManager.get_nonce() is not None


@pytest.mark.staging
@pytest.mark.asyncio
async def test_nonce_context(aiosession, staging_directory, event_loop):
    asyncio.set_event_loop(event_loop)
    url = staging_directory["newNonce"]
    nonceManager = NonceManager(url=url, session=aiosession)
    async with nonceManager:
        assert nonceManager.initialized
        await asyncio.sleep(5)
        assert nonceManager.queue.qsize() == 10
        assert await nonceManager.get_nonce() != ""
        assert nonceManager.queue.qsize() == 9
    assert not nonceManager.initialized


@pytest.mark.staging
@pytest.mark.asyncio
async def test_nonce_exhaustion(aiosession, staging_directory, event_loop):
    asyncio.set_event_loop(event_loop)
    url = staging_directory["newNonce"]
    nonceManager = NonceManager(url=url, session=aiosession)
    async with nonceManager:
        for _ in range(11):
            await nonceManager.get_nonce()
