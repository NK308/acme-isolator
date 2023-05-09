from .base import ACME_Object
from .challenge import ACME_Challenge
from .identifier import ACME_Identifier
from dataclasses import dataclass, field, InitVar


@dataclass(order=False, kw_only=True)
class ACME_Authorization(ACME_Object):
    identifier: ACME_Identifier = field(init=False)
    identifier: InitVar[dict]
    status: str
    expires: str|None
    challenges: list[ACME_Challenge] | list[dict]
    wildcard: bool|None
    url: str

    def __post_init__(self, identifier):
        self. identifier = ACME_Identifier.parse(identifier)

    #TODO translate challanges from json to objects
