from .base import ACME_Object
from dataclasses import dataclass, field
from .order import ACME_Orders
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
from ..request import JwsKid, JwsJwk


@dataclass(order=False, kw_only=True)
class ACME_Account(ACME_Object):
    status: str
    contact: list[str] | None
    termsOfServiceAgreed: bool | None
    orders: str | ACME_Orders
    resources: dict[str, str]
    parent: None = field(default=None, init=False)

    @classmethod
    async def create_from_key(cls, url: str, key: EllipticCurvePrivateKey):
        pass

    @classmethod
    async def get_from_key(cls, url: str, key: EllipticCurvePrivateKey):
        pass
