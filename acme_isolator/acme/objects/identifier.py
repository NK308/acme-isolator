from abc import ABC
from .base import ACME_Object, ElementList
from dataclasses import dataclass, field
from typing import ClassVar

_identifier_register = dict()


@dataclass(order=False, kw_only=True)
class ACME_Identifier:

    type: ClassVar[str]
    value: str

    def __init_subclass__(cls, **kwargs):
        global _identifier_register
        _identifier_register[cls.type] = cls

    def __call__(self) -> str:
        return self.value

    def as_dict(self) -> dict[str, str]:
        return {"type": self.type, "value": self.value}

    @staticmethod
    def parse(identifier: dict) -> "ACME_Identifier":
        t = identifier.get("type", None)
        if t in _identifier_register.keys():
            return _identifier_register[t](value=identifier["value"])
        else:
            raise ValueError("Unknown/undefined identifier type")


class IdentifierDescriptor:
    def __init__(self, name="identifier"):
        self.name = name

    def __set__(self, instance, value):
        if isinstance(value, ACME_Identifier):
            instance.__dict__[self.name] = value
        else:
            instance.__dict__[self.name] = ACME_Identifier.parse(value)
        # else:
        #     raise ValueError(f"Type {type(value).__name__} not supported for field {self.name}.")

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]


class ACME_Identifier_DNS(ACME_Identifier):
    type: ClassVar[str] = "dns"
