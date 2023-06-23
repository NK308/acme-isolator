from .base import ACME_Object
from abc import ABC
from dataclasses import dataclass


@dataclass
class ACME_Challenge(ACME_Object):
    type: str
    status: str
    validated: None | str
    error: None | dict | list | str
    # For now this is just a stub
    #TODO add concrete implementation for dns challenge

    def keyAuthorization(self) -> str:
        #TODO implement rfc7638
        pass


class ACME_Challenge_dns_01(ACME_Challenge):
    token: str
    type: str = "dns-01"