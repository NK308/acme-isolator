import pytest
import asyncio
import aiohttp
from aiohttp import web, connector
import ssl
import trustme

@pytest.fixture
def tls_certificate_authority():
    return trustme.CA()

@pytest.fixture
def tls_certificate(tls_certificate_authority):
    return tls_certificate_authority.issue_server_cert("localhost", "127.0.0.1", "::1")

@pytest.fixture
def server_ssl_ctx(tls_certificate) -> ssl.SSLContext:
    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    tls_certificate.configure_cert(ssl_ctx)
    return ssl_ctx

@pytest.fixture
def client_ssl_ctx(tls_certificate_authority) -> ssl.SSLContext:
    ssl_ctx = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    tls_certificate_authority.configure_trust(ssl_ctx)
    return ssl_ctx


@pytest.fixture
def client_request_redirection(client_ssl_ctx, monkeypatch):
    monkeypatch.setitem(aiohttp.connector.TCPConnector.__init__.__kwdefaults__, "ssl_context", client_ssl_ctx)


@pytest.fixture
async def create_https_server(app: web.Application, server_ssl_ctx) -> web.TCPSite:
    runner = web.AppRunner(app)
    site = web.TCPSite(runner, "localhost", 443, ssl_context=server_ssl_ctx)
    await site.start()
    yield site
    await site.stop()
