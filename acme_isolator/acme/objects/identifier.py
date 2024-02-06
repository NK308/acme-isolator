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

    def __set__(self, instance, value):
        if isinstance(value, ACME_Identifier):
            instance.__dict__[self.name] = value
        else:
            instance.__dict__[self.name] = ACME_Identifier.parse(value)
        # else:
        #     raise ValueError(f"Type {type(value).__name__} not supported for field {self.name}.")

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]


class IdentifierListDescriptor:
    def __set__(self, instance, value):
        if isinstance(value, list):
            l = list()
            for e in value:
                if isinstance(e, ACME_Identifier):
                    l.append(e)
                elif isinstance(e, dict):
                    l.append(ACME_Identifier.parse(e))
                else:
                    raise ValueError
            instance.__dict__[self.name] = l
        else:
            raise ValueError

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set_name__(self, owner, name):
        self.name = name


class ACME_Identifier_DNS(ACME_Identifier):
    type: ClassVar[str] = "dns"
    type: str = "dns"
