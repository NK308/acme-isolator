from acme_isolator.acme.request import jws


def test_string2utf8():
    test_string = '{"typ":"JWT",\r\n "alg":"HS256"}' # example taken from rfc7515 A.1.1
    result_list = [123, 34, 116, 121, 112, 34, 58, 34,
                   74, 87, 84, 34, 44, 13, 10, 32,
                   34, 97, 108, 103, 34, 58, 34, 72,
                   83, 50, 53, 54, 34, 125]
    assert [int(x) for x in jws.JwsBase._encode_string2utf8(test_string)] == result_list


def test_utf82base64():
    input_list = [123, 34, 116, 121, 112, 34, 58, 34,
                   74, 87, 84, 34, 44, 13, 10, 32,
                   34, 97, 108, 103, 34, 58, 34, 72,
                   83, 50, 53, 54, 34, 125]
    assert jws.JwsBase._encode_bytes2base64(bytes(input_list)) == "eyJ0eXAiOiJKV1QiLA0KICJhbGciOiJIUzI1NiJ9"


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

