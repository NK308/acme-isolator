from .base import ACME_Object
from .challenge import ACME_Challenge
from dataclasses import dataclass, field, InitVar


@dataclass(order=False, kw_only=True)
class ACME_Authorization(ACME_Object):
    identifier: str = field(init=False)
    identifier: InitVar[dict]
    identifier_type: str = field(init=False)
    status: str
    expires: str|None
    challenges: list[ACME_Challenge] | list[dict]
    wildcard: bool|None

    def __post_init__(self, identifier):
        self.identifier_type = identifier["type"]
        self.identifier = identifier["value"]

    #TODO translate challanges from json to objects
