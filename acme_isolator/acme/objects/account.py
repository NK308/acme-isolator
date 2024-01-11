from .base import ACME_Object
from dataclasses import dataclass, field
from .order import ACME_Orders
from ..request.session import Session
from ..request import JwsKid, JwsJwk
from jwcrypto.jwk import JWK
import sys


@dataclass(order=False, kw_only=True)
class ACME_Account(ACME_Object):
    key: JWK
    session: Session
    status: str
    contact: list[str] | None
    orders: str | ACME_Orders
    parent: None = field(default=None, init=False)

    async def request(self, url: str, payload: dict | None):
        nonce = await self.session.nonce_pool.get_nonce()
        request_builder = JwsKid(kid=self.url, key=self.key, payload=payload, nonce=nonce, url=url)
        return await self.session.post(url, payload=request_builder.build())

    async def fetch_orders(self):
        if type(self.orders) == str:
            url = self.orders
            data, status = await self.request(url, None)
            if status == 200:
                self.orders = ACME_Orders(url=url, parent=self, **data)
            else:
                raise ConnectionError(f"Server returned status code {status} while fetching orders from {url}.")
        elif type(self.orders) == ACME_Orders:
            await self.orders.update()
        await self.orders.update_orders()

    @property
    def account(self):
        return self

    @classmethod
    async def get_from_url(cls, parent_object: ACME_Object, url: str):
        raise NotImplementedError("Class ACME_Account has not get_from _url classmethod.")

    @classmethod
    async def create_from_key(cls, session: Session, key: JWK, contact: list[str]):
        payload = {"termsOfServiceAgreed": True, "contact": contact}
        nonce = await session.nonce_pool.get_nonce()
        url = session.directory.newAccount
        req = JwsJwk(payload=payload, nonce=nonce, key=key, url=url).build()
        async with session.resource_sessions["newAccount"].post(url=url, data=req, headers={"User-Agent": "agent", "Content-Type": "application/jose+json"}) as resp:
            try:
                assert resp.status == 201, f"{resp.status} {await resp.json()}" # Maybe warning, if the account already exists
                data = await resp.json()
                new_nonce = resp.headers["Replay-Nonce"]
                session.nonce_pool.put_nonce(new_nonce)
                return ACME_Account(url=resp.headers["Location"], session=session, **data)
            except AssertionError:
                print(f"Got HTTP status code {resp.status} (201 expected)", file=sys.stderr)
                print(await resp.json(), file=sys.stderr)

    @classmethod
    async def get_from_key(cls, session: Session, key: JWK):
        payload = {"onlyReturnExisting": True}
        nonce = await session.nonce_pool.get_nonce()
        url = session.directory.newAccount
        req = JwsJwk(payload=payload, nonce=nonce, key=key, url=url).build()
        async with session.resource_sessions["newAccount"].post(url=url, data=req) as resp:
            assert resp.status == 200
            data = await resp.json()
            new_nonce = resp.headers["Replay-Nonce"]
            session.nonce_pool.put_nonce(new_nonce)
            return ACME_Account(key=key, url=resp.headers["Location"], session=session, **data)
