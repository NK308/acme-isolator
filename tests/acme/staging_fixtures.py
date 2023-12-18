import pytest
import pytest_asyncio
from aiohttp import ClientSession
from tests.acme.key_generation import generate_key_pair
from acme_isolator.acme.request.session import Session

directory_resource_json = { # json stolen from the LetsEncrypt staging environment
    "keyChange": "https://acme-staging-v02.api.letsencrypt.org/acme/key-change",
    "meta": {
        "caaIdentities": [
            "letsencrypt.org"
        ],
        "termsOfService": "https://letsencrypt.org/documents/LE-SA-v1.3-September-21-2022.pdf",
        "website": "https://letsencrypt.org/docs/staging-environment/"
    },
    "newAccount": "https://acme-staging-v02.api.letsencrypt.org/acme/new-acct",
    "newNonce": "https://acme-staging-v02.api.letsencrypt.org/acme/new-nonce",
    "newOrder": "https://acme-staging-v02.api.letsencrypt.org/acme/new-order",
    "renewalInfo": "https://acme-staging-v02.api.letsencrypt.org/draft-ietf-acme-ari-01/renewalInfo/",
    "revokeCert": "https://acme-staging-v02.api.letsencrypt.org/acme/revoke-cert"
}


@pytest_asyncio.fixture()
async def aiosession(event_loop):
    s = ClientSession()
    async with s:
        yield s


@pytest.fixture
def staging_api_url():
    return "https://acme-staging-v02.api.letsencrypt.org/directory"


@pytest_asyncio.fixture()
async def staging_directory(staging_api_url, aiosession):
    resp = await aiosession.get(staging_api_url)
    async with resp:
        yield await resp.json()


@pytest_asyncio.fixture()
async def staging_session_without_account(staging_api_url):
    async with Session(staging_api_url) as session:
        yield session


@pytest_asyncio.fixture()
async def staging_session(staging_api_url, generate_key_pair):
    async with Session(staging_api_url) as session:
        yield session
