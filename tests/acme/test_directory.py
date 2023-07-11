import pytest
from acme_isolator.acme.objects.directory import ACME_Directory
from .staging_fixtures import directory_resource_json


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
async def test_directory_parsing(client_request_redirection, create_https_server):
    d = await ACME_Directory.get_directory("https://localhost/directory")
    assert d.newNonce == directory_resource_json["newNonce"]
    assert d.newAccount == directory_resource_json["newAccount"]


@pytest.mark.staging
@pytest.mark.asyncio
async def test_directory_fetching():
    d = await ACME_Directory.get_directory("https://acme-staging-v02.api.letsencrypt.org/directory")
    assert d.newNonce == directory_resource_json["newNonce"]
    assert d.newAccount == directory_resource_json["newAccount"]
    assert type(d) == ACME_Directory
