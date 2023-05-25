from .base import ACME_Object
from dataclasses import dataclass, field
from .order import ACME_Orders
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
from ..request.session import Session
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
    async def create_from_key(cls, session: Session, key: EllipticCurvePrivateKey, contact: list[str]):
        payload = {"termsOfServiceAgreed": True, "contact": contact}
        nonce = await session.nonce_pool.get_nonce()
        url = session.directory.newAccount
        req = JwsJwk(payload=payload, nonce=nonce, key=key, url=url).build()
        async with session.resource_sessions["newAccount"].post(url=url, data=req) as resp:
            assert resp.status == 201 # Maybe warning, if the account already exists
            data = await resp.json()
            new_nonce = resp.headers["Replay-Nonce"]
            session.nonce_pool.put_nonce(new_nonce)
            return ACME_Account(**data)


    @classmethod
    async def get_from_key(cls, session: Session, key: EllipticCurvePrivateKey):
        payload = {"onlyReturnExisting": True}
        nonce = await session.nonce_pool.get_nonce()
        url = session.directory.newAccount
        req = JwsJwk(payload=payload, nonce=nonce, key=key, url=url).build()
        async with session.resource_sessions["newAccount"].post(url=url, data=req) as resp:
            assert resp.status == 200
            data = await resp.json()
            new_nonce = resp.headers["Replay-Nonce"]
            session.nonce_pool.put_nonce(new_nonce)
            return ACME_Account(**data)
