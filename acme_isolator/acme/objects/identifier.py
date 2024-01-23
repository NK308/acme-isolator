from abc import ABC
from .base import ACME_Object, ElementList
from dataclasses import dataclass, field
from typing import ClassVar

_identifier_register = dict()

@dataclass(order=False, kw_only=True)
class ACME_Identifier(ACME_Object):
    type: ClassVar[str]
    value: str

    def __init_subclass__(cls, **kwargs):
        global _identifier_register
        _identifier_register[cls.type] = cls

    def __call__(self) -> str:
        return self.value

    @staticmethod
    def parse(identifier: dict) -> "ACME_Identifier":
        t = identifier.get("type", None)
        if t in _identifier_register.keys():
            return _identifier_register[t](identifier)
        else:
            raise ValueError("Unknown/undefined identifier type")


class ACME_Identifier_DNS(ACME_Identifier):
    type: ClassVar[str] = "dns"
