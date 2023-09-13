import pytest
from jwcrypto.jwk import JWK


@pytest.fixture()
def generate_key_pair() -> JWK:
    return JWK.generate(kty="EC", size=265)
