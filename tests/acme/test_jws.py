from acme_isolator.acme.request import jws



def test_jwk_bytes_constructor(generate_key_pair, random_payload, random_nonce):
    jws.JwsJwk(nonce=random_nonce, key=generate_key_pair, payload=random_payload, url="https://example.com/example_url")


def test_jwk_string_constructor(generate_key_pair, random_payload_str, random_nonce):
    jws.JwsJwk(nonce=random_nonce, key=generate_key_pair, payload=random_payload_str, url="https://example.com/example_url")


def test_jwk_empty_constructor(generate_key_pair, random_nonce):
    jws.JwsJwk(nonce=random_nonce, key=generate_key_pair, payload=b"", url="https://example.com/example_url")


def test_jwk_none_constructor(generate_key_pair, random_nonce):
    jws.JwsJwk(nonce=random_nonce, key=generate_key_pair, url="https://example.com/example_url")


def test_jwk_sign(generate_key_pair, random_payload, random_nonce):
    jws.JwsJwk(nonce=random_nonce, key=generate_key_pair, payload=random_payload, url="https://example.com/example_url").build()


def test_kid_string_constructor(generate_key_pair, random_payload_str, random_nonce):
    jws.JwsKid(nonce=random_nonce, kid="46590455", key=generate_key_pair, payload=random_payload_str, url="https://example.com/example_url")

