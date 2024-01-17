from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from jwcrypto.jwk import JWK
from jwcrypto.jws import JWS
from jwcrypto.common import json_encode, base64url_encode

CONTENT_TYPE = "application/jose+json"


@dataclass(kw_only=True)
class JwsBase(ABC):
    nonce: str = field(default="", init=False)
    url: str
    key: JWK
    payload: dict | bytes | None = None
    alg: str = field(default="ES256", init=False, repr=False)
    jws: JWS = None

    def __post_init__(self):
        if type(self.payload) == bytes:
            payload = self.payload
        elif self.payload is None:
            payload = b""
        else:
            payload = json_encode(self.payload)
        self.jws = JWS(payload=payload)

    def build(self, nonce: str) -> bytes:
        self.nonce = nonce
        self.jws.add_signature(self.key, self.alg, protected=self.create_headers())
        return self.jws.serialize(compact=False).encode("utf-8")

    def reset_build(self):
        self.nonce = ""
        del self.jws.objects["protected"]
        # del self.jws.objects["signatures"]
        del self.jws.objects["signature"]

    @abstractmethod
    def create_headers(self):
        return {"alg": self.alg, "nonce": self.nonce, "url": self.url}


@dataclass(kw_only=True)
class JwsJwk(JwsBase):

    def create_headers(self):
        header = super().create_headers()
        header["jwk"] = self.key.export_public(as_dict=True)
        return header


@dataclass(kw_only=True)
class JwsKid(JwsBase):
    kid: str = field(init=True, default=None)

    def create_headers(self):
        header = super().create_headers()
        header["kid"] = self.kid
        return header


@dataclass(kw_only=True)
class JwsRolloverRequest(JwsJwk):
    account: str = field(init=True, default=None)
    oldKey: JWK = field(init=True, default=None)
    payload = None

    def build_payload(self):
        return base64url_encode(json_encode({"account": self.account, "oldKey": self.oldKey.export_public(as_dict=True)}))

    def create_headers(self):
        d = super().create_headers()
        del d["nonce"]
        return d

    def build(self) -> bytes:
        self.payload = self.build_payload()
        return super().build("")
