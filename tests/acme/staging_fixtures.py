import pytest
import pytest_asyncio
from aiohttp import ClientSession

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


@pytest_asyncio.fixture()
async def staging_directory(aiosession):
    resp = await aiosession.get("https://acme-staging-v02.api.letsencrypt.org/directory")
    async with resp:
        yield await resp.json()
