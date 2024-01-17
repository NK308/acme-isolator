import pytest
from jwcrypto.jwk import JWK


@pytest.fixture()
def generate_key_pair(request) -> list[JWK]:
    marker = request.node.get_closest_marker("key_count")
    if marker is None:
        n = 1
    else:
        n = marker.args[0]
    return [JWK.generate(kty="EC", size=265) for _ in range(n)]
