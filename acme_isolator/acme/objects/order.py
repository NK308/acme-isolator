from .base import ACME_Object, ElementList, _object_register
from .descriptors import ListDescriptor, Status, StatusDescriptor, IdentifierListDescriptor
from .exceptions import UnexpectedResponseException
from .identifier import ACME_Identifier
from .authorization import ACME_Authorization, ACME_Authorizations
from cryptography.x509 import CertificateSigningRequest, DNSName, SubjectAlternativeName
from dataclasses import dataclass, field, InitVar
from asyncio import gather, create_task


class OrderStatus(Status):
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
    identifiers: list[ACME_Identifier] = field(default=IdentifierListDescriptor())
    notBefore: str | None = None
    notAfter: str | None = None
    error: dict | None = None
    finalize: str
    certificate: str | None = None

    async def finalization_request(self, csr: CertificateSigningRequest):  # TODO Implement methid for finalizing the order, after class for CSR is defined
        raise NotImplementedError

    def check_csr(self, csr: CertificateSigningRequest) -> bool:
        identifiers = set(self.identifiers)
        for a in csr.extensions.get_extension_for_class(SubjectAlternativeName).get_values_for_type(DNSName):
            for b in identifiers:
                if b == a:
                    c = b
                    break
            else:
                return False
            identifiers.remove(c)
        return len(identifiers) == 0


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
            _object_register[location] = order
            return order
        except AssertionError:
            raise UnexpectedResponseException(status, response=resp).convert_exception()
