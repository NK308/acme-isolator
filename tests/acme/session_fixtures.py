import pytest
import pytest_asyncio
from .pebble_fixtures import pebble_CA_injection, pebble_process
from aiohttp import ClientSession
from acme_isolator.acme.objects.directory import ACME_Directory
from acme_isolator.acme.request.session import Session


@pytest_asyncio.fixture()
async def pebble_directory(pebble_process, pebble_CA_injection, pebble_api_url) -> ACME_Directory:
    return await ACME_Directory.get_directory(pebble_api_url)



@pytest_asyncio.fixture
async def aiosession(event_loop, pebble_CA_injection) -> ClientSession:
    s = ClientSession()
    async with s:
        yield s


@pytest_asyncio.fixture()
async def pebble_session_without_account(event_loop, pebble_process, pebble_api_url, pebble_CA_injection) -> Session:
    async with Session(pebble_api_url) as session:
        yield session
