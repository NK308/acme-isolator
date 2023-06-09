from base64 import urlsafe_b64encode
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from json import dumps
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.asymmetric.ec import ECDSA, EllipticCurvePrivateKey

CONTENT_TYPE = "application/jose+json"


@dataclass(kw_only=True)
class JwsBase(ABC):
    nonce: str
    url: str
    key: EllipticCurvePrivateKey
    payload: dict | bytes | None = None
    alg: str = "ES256"

    @staticmethod
    def _encode_bytes2base64(data: bytes) -> str:
        return urlsafe_b64encode(data).decode("ascii").strip("=")

    @staticmethod
    def _encode_string2utf8(s: str) -> bytes:
        return s.encode("utf-8")

    def build(self) -> bytes:
        header = self._encode_bytes2base64(self._encode_string2utf8(dumps(self.create_headers())))
        if self.payload is None:
            payload = ""
        else:
            payload = self._encode_bytes2base64(self.create_payload())
        serialized = ".".join([header, payload]).encode("ascii")
        signature = self._encode_bytes2base64(self.key.sign(serialized, ECDSA(SHA256())))
        return dumps({"protected": header, "payload": payload, "signature": signature}).encode("ascii")

    def create_payload(self) -> bytes:
        if isinstance(self.payload, bytes):
            return self.payload
        else:
            return dumps(self.payload).encode("utf-8")

    @abstractmethod
    def create_headers(self):
        return {"alg": self.alg, "nonce": self.nonce, "url": self.url}


@dataclass(kw_only=True)
class JwsJwk(JwsBase):
    jwk: dict = field(init=False, default_factory=dict)

    def __post_init__(self):
        numbers = self.key.public_key().public_numbers()
        self.jwk = dict(crv="P-256", kty="EC")
        self.jwk["x"] = self._encode_bytes2base64(numbers.x.to_bytes(32, "big", signed=False))
        self.jwk["y"] = self._encode_bytes2base64(numbers.y.to_bytes(32, "big", signed=False))

    def create_headers(self):
        header = super().create_headers()
        header["jwk"] = self.jwk
        return header


@dataclass(kw_only=True)
class JwsKid(JwsBase):
    kid: str = field(init=True, default=None)

    def create_headers(self):
        header = super().create_headers()
        header["kid"] = self.kid
        return header
