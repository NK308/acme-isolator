from abc import ABC
from .base import ACME_Object
from dataclasses import dataclass, field


@dataclass(order=False, kw_only=True)
class ACME_Identifier(ABC, ACME_Object):
    type: str = field(init=False)
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
    type: str = field(default="dns", init=False)