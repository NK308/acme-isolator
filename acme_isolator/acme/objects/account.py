from .exceptions import UnexpectedResponseException, ACME_ProblemException
from .base import ACME_Object
from dataclasses import dataclass, field
from .order import ACME_Orders
from ..request.session import Session
from ..request import JwsKid, JwsJwk, JwsRolloverRequest
from jwcrypto.jwk import JWK
import sys

ACCOUNT_VALID = "valid"
ACCOUNT_DEACTIVATED = "deactivated"
ACCOUNT_REVOkED = "revoked"


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
                raise UnexpectedResponseException(status, data )
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
                del data["key"]
                return ACME_Account(url=resp.headers["Location"], key=key, session=session, **data)
            except AssertionError:
                raise UnexpectedResponseException(resp.status, response=await resp.json())

    @classmethod
    async def get_from_key(cls, session: Session, key: JWK):
        payload = {"onlyReturnExisting": True}
        nonce = await session.nonce_pool.get_nonce()
        url = session.directory.newAccount
        req = JwsJwk(payload=payload, nonce=nonce, key=key, url=url).build()
        async with session.resource_sessions["newAccount"].post(url=url, data=req, headers={"User-Agent": "agent", "Content-Type": "application/jose+json"}) as resp:
            try:
                assert resp.status == 200
                data = await resp.json()
                new_nonce = resp.headers["Replay-Nonce"]
                session.nonce_pool.put_nonce(new_nonce)
                del data["key"]
                return ACME_Account(key=key, url=resp.headers["Location"], session=session, **data)
            except AssertionError:
                raise UnexpectedResponseException(resp.status, response=await resp.json()).convert_exception()

    async def post(self, url: str, payload: dict | bytes) -> tuple[dict, int]:
        nonce = await self.session.nonce_pool.get_nonce()
        jws = JwsKid(url=url, kid=self.url, key=self.key, payload=payload, nonce=nonce)
        return await self.session.post(url=url, payload=jws.build())

    async def update_account(self, **updated_payload):
        try:
            resp, status = await self.post(url=self.url, payload=updated_payload)
            assert status == 200
            self.status = resp["status"]
            self.contact = resp["contact"]
            # TODO check if account url has to be updated
        except AssertionError as e:
            raise UnexpectedResponseException(status, response=resp).convert_exception()


    async def deactivate_account(self):
        await self.update_account(status="deactivated")


    async def key_rollover(self, new_key: JWK):
        inner_object = JwsRolloverRequest(url=self.url, key=new_key, oldKey=self.key).build()
        outer_object = JwsKid(url=self.session.directory.keyChange,
                              payload=inner_object,
                              key=self.key,
                              kid=self.url,
                              nonce=await self.session.nonce_pool.get_nonce()).build()
        resp, status = await self.session.post(self.session.directory.keyChange, outer_object)
        assert status == 200
        self.key = new_key
        self.url = resp[""]


