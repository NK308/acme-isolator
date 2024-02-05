from .base import ACME_Object, ElementList, ClassVar, StatusDescriptor
from enum import Enum
from .challenge import ACME_Challenge
from .identifier import ACME_Identifier, IdentifierDescriptor
from dataclasses import dataclass, field, InitVar


class AuthorizationStatus(Enum):
    AUTHORIZATION_PENDING = "pending"
    AUTHORIZATION_VALID = "valid"
    AUTHORIZATION_INVALID = "invalid"
    AUTHORIZATION_DEACTIVATED = "deactivated"
    AUTHORIZATION_EXPIRED = "expired"
    AUTHORIZATION_REVOKED = "revoked"


@dataclass(order=False, kw_only=True)
class ACME_Authorization(ACME_Object):
    identifier: ACME_Identifier = field(default=IdentifierDescriptor())
    status: AuthorizationStatus = field(default=StatusDescriptor(AuthorizationStatus))
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
