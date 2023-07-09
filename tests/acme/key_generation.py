import pytest
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey, SECP256R1, generate_private_key


@pytest.fixture()
def generate_key_pair() -> EllipticCurvePrivateKey:
    return generate_private_key(SECP256R1())
