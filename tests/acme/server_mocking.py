import pytest
import asyncio
import aiohttp
from aiohttp import web, connector
import ssl
from .pebble_fixtures import pebble_CA
import trustme

# @pytest.fixture
# def server_ssl_ctx(tls_certificate) -> ssl.SSLContext:
#     ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
#     tls_certificate.configure_cert(ssl_ctx)
#     return ssl_ctx


@pytest.fixture
def client_ssl_ctx(pebble_CA) -> ssl.SSLContext:
    ssl_ctx = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    ssl_ctx.load_verify_locations(pebble_CA)
    return ssl_ctx


@pytest.fixture
def client_request_redirection(client_ssl_ctx, monkeypatch):
    monkeypatch.setitem(aiohttp.connector.TCPConnector.__init__.__kwdefaults__, "ssl_context", client_ssl_ctx)

