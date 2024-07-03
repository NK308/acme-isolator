from dataclasses import dataclass
from typing import ClassVar
from cryptography.x509 import DNSName

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


class ACME_Identifier_DNS(ACME_Identifier):
    type: ClassVar[str] = "dns"
    type: str = "dns"

    def __eq__(self, other):
        if isinstance(other, self.__class__) or isinstance(other, DNSName):
            return self.value == other.value
        else:
            raise NotImplementedError
