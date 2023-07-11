import pytest
import pytest_asyncio
from aiohttp import ClientSession


@pytest_asyncio.fixture()
async def session(event_loop):
    s = ClientSession()
    async with s:
        yield s


@pytest_asyncio.fixture()
async def staging_directory(session):
    resp = await session.get("https://acme-staging-v02.api.letsencrypt.org/directory")
    async with resp:
        yield await resp.json()
