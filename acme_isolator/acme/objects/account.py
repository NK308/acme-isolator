import json

from .exceptions import UnexpectedResponseException, ACME_ProblemException
from .base import ACME_Object, ClassVar, AcmeObject, _object_register
from .descriptors import AcmeDescriptor, Status, StatusDescriptor
from dataclasses import dataclass, field
from .order import ACME_Orders
from ..request.session import Session
from ..request import JwsBase, JwsKid, JwsJwk, JwsRolloverRequest
from jwcrypto.jwk import JWK
import sys


class AccountStatus(Status):
    ACCOUNT_VALID = "valid"
    ACCOUNT_DEACTIVATED = "deactivated"
    ACCOUNT_REVOKED = "revoked"


@dataclass(order=False, kw_only=True)
class ACME_Account(ACME_Object):
    key: JWK
    session: Session
    status: AccountStatus = field(default=StatusDescriptor(AccountStatus))
    contact: list[str] | None
    orders: ACME_Orders | ACME_Orders.url_class = field(default=AcmeDescriptor(ACME_Orders))
    parent: None = field(default=None, init=False)

    hold_keys: ClassVar[set[str]] = ACME_Object.hold_keys | {"key"}

    @staticmethod
    def complete_dict(response_url: str, key: JWK, **additional_fields) -> dict:
        d = super().complete_dict(response_url=response_url, **additional_fields)
        d["orders"] = ACME_Orders.url_class(d["orders"])
        return d

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
    async def get_from_url(cls, parent_object: ACME_Object, url: str, **additional_fields):
        raise NotImplementedError("Class ACME_Account has not get_from _url classmethod.")

    @classmethod
    async def create_from_key(cls, session: Session, key: JWK, contact: list[str]):
        payload = {"termsOfServiceAgreed": True, "contact": contact}
        nonce = await session.nonce_pool.get_nonce()
        url = session.directory.newAccount
        req = JwsJwk(payload=payload, key=key, url=url)
        try:
            resp, status, location = await session.post(req)
            data = resp.copy()
            data.update({"key": key, "url": location})
            if location in _object_register:
                o = _object_register[location]
                await o.update_fields(data)
            else:
                o = ACME_Account(session=session, **data)
            return o
        except AssertionError:
            raise UnexpectedResponseException(status, resp).convert_exception()

    @classmethod
    async def get_from_key(cls, session: Session, key: JWK):
        payload = {"onlyReturnExisting": True}
        url = session.directory.newAccount
        req = JwsJwk(payload=payload, key=key, url=url)
        try:
            resp, status, location = await session.post(req)
            assert status == 200
            data = resp.copy()
            data.update({"key": key, "url": location})
            if location in _object_register:
                o = _object_register[location]
                await o.update_fields(data)
            else:
                o = ACME_Account(session=session, **data)
            return o
        except AssertionError:
            raise UnexpectedResponseException(status, response=resp).convert_exception()

    async def post(self, url: str, payload: dict | bytes | None, empty_response: bool = False) -> tuple[dict, int, str]:
        req = JwsKid(url=url, kid=self.url, key=self.key, payload=payload)
        return await self.session.post(req, empty_response=empty_response)

    async def update_account(self, **updated_payload):
        try:
            resp, status, location = await self.post(url=self.url, payload=updated_payload)
            assert status == 200
            await self.update_fields(resp)
            # TODO check if account url has to be updated
        except AssertionError as e:
            raise UnexpectedResponseException(status, response=resp).convert_exception()


    async def deactivate_account(self):
        await self.update_account(status="deactivated")


    async def key_rollover(self, new_key: JWK):
        url = self.session.directory.keyChange
        inner_object = JwsRolloverRequest(url=url, account=self.url, key=new_key, oldKey=self.key).build("")
        try:
            resp, status, location = await self.post(url=url, payload=json.loads(inner_object), empty_response=True)
            assert status == 200
            self.key = new_key
        except AssertionError:
            raise UnexpectedResponseException(status, response=resp).convert_exception()


