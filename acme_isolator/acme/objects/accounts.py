from .base import ACME_Object
from dataclasses import dataclass


@dataclass
class ACME_Account(ACME_Object):
    status: str
    contact: list[str]|None
    termsOfServiceAgreed: bool|None
    orders: str