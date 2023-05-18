from .base import ACME_Object
from dataclasses import dataclass
from .order import ACME_Orders


@dataclass(order=False, kw_only=True)
class ACME_Account(ACME_Object):
    status: str
    contact: list[str] | None
    termsOfServiceAgreed: bool | None
    orders: str | ACME_Orders
