from .base import ACME_Object, ElementList, StatusDescriptor
from enum import Enum
from .challenge import ACME_Challenge
from .identifier import ACME_Identifier, IdentifierDescriptor
from dataclasses import dataclass, field


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

    #TODO translate challanges from json to objects


@dataclass
class ACME_Authorizations(ElementList[ACME_Authorization]):
    pass
