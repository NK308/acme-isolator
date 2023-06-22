import pytest
import aiohttp

class MockDirectoryResourceResponse:

    @staticmethod
    def raise_for_status():
        return ""

    @staticmethod
    async def json(*args, **kwargs):
        return { # json stolen from the LetsEncrypt staging environment
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


@pytest.fixture()
def mock_directory_resource(monkeypatch):
    async def get_mock_response():
        return MockDirectoryResourceResponse()
    monkeypatch.setattr(aiohttp, "request", mock_directory_resource)
