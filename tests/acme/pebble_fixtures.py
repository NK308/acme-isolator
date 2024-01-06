import aiohttp.connector
import pytest
import pytest_asyncio
from xprocess import ProcessStarter
# from tests.acme.key_generation import generate_key_pair
import ssl
from pathlib import Path

PEBBLE_CA_PATH = "./pebble/test/certs/pebble.minica.pem"
PEBBLE_URL = "https://localhost:14000/dir"


@pytest.fixture(autouse=True)
def pebble_CA_path() -> Path:
    return Path(PEBBLE_CA_PATH)


@pytest.fixture(autouse=True)
def pebble_ssl_context(pebble_CA_path) -> ssl.SSLContext:
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.load_verify_locations(pebble_CA_path)
    return ssl_ctx


@pytest.fixture
def pebble_CA_injection(pebble_ssl_context, monkeypatch):
    monkeypatch.setitem(aiohttp.connector.TCPConnector.__init__.__kwdefaults__, "ssl_context", pebble_ssl_context)


@pytest.fixture(autouse=True)
def pebble_api_url() -> str:
    return PEBBLE_URL


@pytest.fixture
def pebble_process(xprocess):
    class PebbleStarter(ProcessStarter):
        args = ["/usr/bin/go", "run", "./cmd/pebble"]
        popen_kwargs = {"cwd": "./pebble",
                        "shell": False}
        terminate_on_interrupt = True
        pattern = r"Pebble \d+/\d+/\d+ \d+:\d+:\d+ Listening on: .*"
        timeout = 10

        def startup_check(self):
            return True # TODO maybe add an actual test

    process_name = "pebble"
    xprocess.ensure(process_name, PebbleStarter)
    yield

    xprocess.getinfo(process_name).terminate()

