import pytest
import aiohttp
from acme_isolator.acme.objects.directory import ACME_Directory
directory_resource_json = { # json stolen from the LetsEncrypt staging environment
            "NW9luPYOK8w": "https://community.letsencrypt.org/t/adding-random-entries-to-the-directory/33417",
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

class MockDirectoryResourceResponse:

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @staticmethod
    def raise_for_status():
        return ""

    @staticmethod
    async def json(*args, **kwargs):
        return directory_resource_json


@pytest.fixture()
def mock_directory_resource(monkeypatch):
    async def get_mock_response(*args, **kwargs):
        return MockDirectoryResourceResponse()
    monkeypatch.setattr("aiohttp.request", get_mock_response)


@pytest.mark.asyncio
async def test_directory_parsing(mock_directory_resource):
    d = await ACME_Directory.get_directory("https://acme-staging-v02.api.letsencrypt.org/directory")
    assert d.newNonce == directory_resource_json["newNonce"]
    assert d.newAccount == directory_resource_json["newAccount"]


@pytest.mark.asyncio
async def test_directory_fetching():
    d = await ACME_Directory.get_directory("https://acme-staging-v02.api.letsencrypt.org/directory")
    assert d.newNonce == directory_resource_json["newNonce"]
    assert d.newAccount == directory_resource_json["newAccount"]
    assert type(d) == ACME_Directory
