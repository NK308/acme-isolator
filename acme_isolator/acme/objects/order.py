from .base import ACME_Object
from .identifier import ACME_Identifier
from .authorization import ACME_Authorization
from dataclasses import dataclass, field, InitVar
from collections.abc import Sequence


@dataclass(order=False, kw_only=True)
class ACME_Order(ACME_Object):
    status: str
    expires: str
    identifier: ACME_Identifier = field(init=False)
    identifier: InitVar[dict]
    notBefore: str | None
    notAfter: str | None
    error: dict | None
    authorizations: list[str] | list[ACME_Authorization]
    finalize: str
    certificate: str | None

    def __post_init__(self, identifier: dict):
        self.identifier = ACME_Identifier.parse(identifier)


@dataclass(order=False, kw_only=True)
class ACME_Orders(ACME_Object, Sequence):
    orders: list[str] | list[ACME_Order]

    def __getitem__(self, i):
        return self.orders[i]

    def __len__(self):
        return len(self.orders)

    def __iter__(self):
        return self.orders.__iter__()
