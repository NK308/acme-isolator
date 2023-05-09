from .base import ACME_Object
from abc import ABC
from dataclasses import dataclass


@dataclass
class ACME_Challenge(ABC, ACME_Object):
    # For now this is just a stub
    #TODO add concrete implementation for dns challenge
    pass