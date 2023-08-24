import aiohttp.connector
import pytest
import pytest_asyncio
from aiohttp import ClientSession
from tests.acme.key_generation import generate_key_pair
from acme_isolator.acme.request.session import Session
import ssl


@pytest_asyncio.fixture
async def aiosession(event_loop, pebble_CA_injection):
    s = ClientSession()
    async with s:
        yield s


@pytest.fixture
def pebble_api_url() -> str:
    return "https://localhost:14000/dir"


@pytest.fixture
def pebble_ssl_context() -> ssl.SSLContext:
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.load_verify_locations("/home/nk/git/pebble/test/certs/pebble.minica.pem")
    return ssl_ctx


@pytest.fixture
def pebble_CA_injection(pebble_ssl_context, monkeypatch):
    monkeypatch.setitem(aiohttp.connector.TCPConnector.__init__.__kwdefaults__, "ssl_context", pebble_ssl_context)


@pytest_asyncio.fixture()
async def pebble_directory(pebble_api_url, aiosession):
    resp = await aiosession.get(pebble_api_url)
    async with resp:
        yield await resp.json()


@pytest_asyncio.fixture()
async def pebble_session_without_account(pebble_api_url, pebble_CA_injection):
    async with Session(pebble_api_url) as session:
        yield session


@pytest_asyncio.fixture()
async def pebble_session(pebble_api_url, generate_key_pair):
    async with Session(pebble_api_url) as session:
        yield session
