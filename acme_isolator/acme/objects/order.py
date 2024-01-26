from enum import Enum
from .base import ACME_Object, ACME_List, ClassVar
from .exceptions import UnexpectedResponseException
from .identifier import ACME_Identifier
from .authorization import ACME_Authorization, ACME_Authorizations
from dataclasses import dataclass, field, InitVar
from asyncio import gather, create_task


class OrderStatus(Enum):
    PENDING = "pending"
    READY = "ready"
    PROCESSING = "processing"
    VALID = "valid"
    INVALID = "invalid"


@dataclass(order=False, kw_only=True)
class ACME_Order(ACME_Object):
    status: OrderStatus
    status: InitVar[str]
    expires: str | None = None
    authorizations: ACME_Authorizations
    authorizations: InitVar[list[dict]]
    identifiers: list[ACME_Identifier]
    identifiers: InitVar[list[dict]]
    notBefore: str | None = None
    notAfter: str | None = None
    error: dict | None = None
    finalize: str
    certificate: str | None = None

    def __post_init__(self, authorizations: list[dict], identifiers: list[dict]):
        self.identifiers = [ACME_Identifier.parse(identifier) for identifier in identifiers]
        self.authorizations = ACME_Authorizations(*authorizations, parent=self.parent)

    # TODO finalize order


@dataclass
class ACME_Orders(ACME_List[ACME_Order]):
    convert_table: ClassVar[dict] = {"orders": ACME_Order}

    orders: InitVar[list[dict]]

    async def create_order(self, identifiers: list[ACME_Identifier], notBefore: str | None = None, notAfter: str | None = None):
        payload = {"notBefore": notBefore, "notAfter": notAfter}
        payload["identifiers"] = [id.as_dict() for id in identifiers]
        try:
            resp, status, location = await self.account.post(self.account.session.directory.newOrder, payload=payload)
            assert status == 201
            resp.update({"url": location})
            order = ACME_Order(parent=self, **resp)
            self._list.append(order)
            return order
        except AssertionError:
            raise UnexpectedResponseException(status, response=resp).convert_exception()
