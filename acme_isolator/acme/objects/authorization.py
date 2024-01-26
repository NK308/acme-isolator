from enum import Enum
from .base import ACME_Object, ElementList, ClassVar
from .challenge import ACME_Challenge
from .identifier import ACME_Identifier
from dataclasses import dataclass, field, InitVar


class AuthorizationStatus(Enum):
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"
    DEACTIVATED = "deactivated"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass(order=False, kw_only=True)
class ACME_Authorization(ACME_Object):
    identifier: ACME_Identifier = field(init=False)
    identifier: InitVar[dict]
    status: AuthorizationStatus = field(init=False)
    status: InitVar[str]
    expires: str | None
    challenges: list[ACME_Challenge] | list[dict]
    wildcard: bool | None

    def __post_init__(self, identifier: dict):
        self.identifier = ACME_Identifier.parse(identifier)

    #TODO translate challanges from json to objects


@dataclass
class ACME_Authorizations(ElementList[ACME_Authorization]):
    # convert_table: ClassVar[dict] = {"authorizations": ACME_Authorization}

    pass
