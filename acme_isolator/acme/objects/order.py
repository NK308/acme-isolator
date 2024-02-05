from .base import ACME_Object, ElementList, ClassVar, StatusDescriptor, ListDescriptor
from enum import Enum
from .exceptions import UnexpectedResponseException
from .identifier import ACME_Identifier, IdentifierDescriptor
from .authorization import ACME_Authorization, ACME_Authorizations
from dataclasses import dataclass, field, InitVar
from asyncio import gather, create_task


class OrderStatus(Enum):
    ORDER_PENDING = "pending"
    ORDER_READY = "ready"
    ORDER_PROCESSING = "processing"
    ORDER_VALID = "valid"
    ORDER_INVALID = "invalid"


@dataclass(order=False, kw_only=True)
class ACME_Order(ACME_Object):
    status: OrderStatus = field(default=StatusDescriptor(OrderStatus))
    expires: str | None = None
    authorizations: ACME_Authorizations = field(default=ListDescriptor(ACME_Authorizations))
    identifiers: list[ACME_Identifier]
    identifiers: InitVar[list[dict]]
    notBefore: str | None = None
    notAfter: str | None = None
    error: dict | None = None
    finalize: str
    certificate: str | None = None

    def __post_init__(self,identifiers: list[dict]):
        self.identifiers = [ACME_Identifier.parse(identifier) for identifier in identifiers]

    # TODO finalize order


class OrderSet(ElementList[ACME_Order]):
    pass

@dataclass
class ACME_Orders(ACME_Object):
    _order_set: OrderSet = field(init=False)

    orders: InitVar[list[str]]

    def __post_init__(self, orders: list[str]):
        self._order_set = OrderSet(orders, parent=self)
        self.__iter__ = self._order_set.__iter__
        self.__len__ = self._order_set.__len__
        self.__contains__ = self._order_set.__contains__
        self.add = self._order_set.add
        self.remove = self._order_set.remove
        self.discard = self._order_set.discard

    async def create_order(self, identifiers: list[ACME_Identifier], notBefore: str | None = None, notAfter: str | None = None):
        payload = {"notBefore": notBefore, "notAfter": notAfter}
        payload["identifiers"] = [id.as_dict() for id in identifiers]
        try:
            resp, status, location = await self.account.post(self.account.session.directory.newOrder, payload=payload)
            assert status == 201
            resp.update({"url": location})
            order = ACME_Order(parent=self, **resp)
            self._order_set.add(order)
            return order
        except AssertionError:
            raise UnexpectedResponseException(status, response=resp).convert_exception()
