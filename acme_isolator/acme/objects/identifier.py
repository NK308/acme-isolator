from abc import ABC
from .base import ACME_Object
from dataclasses import dataclass, field
from typing import ClassVar


@dataclass(order=False, kw_only=True)
class ACME_Identifier(ACME_Object):
    type: ClassVar[str]
    value: str

    def __call__(self) -> str:
        return self.value

    @staticmethod
    def parse(identifier: dict) -> "ACME_Identifier":
        if identifier["type"] == "dns":
            return ACME_Identifier_DNS(**identifier)
        else:
            raise ValueError("Unknown/undefined identifier type")



class ACME_Identifier_DNS(ACME_Identifier):
    type: ClassVar[str] = "dns"