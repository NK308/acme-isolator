from .base import ACME_Object, ElementList
from .descriptors import Status, StatusDescriptor, IdentifierDescriptor, ListDescriptor
from .challenge import ACME_Challenge, ACME_Challenges
from .identifier import ACME_Identifier
from dataclasses import dataclass, field


class AuthorizationStatus(Status):
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
    challenges: ACME_Challenges = field(default=ListDescriptor(ACME_Challenges))
    wildcard: bool | None

    async def deactivate(self):
        resp, code, location = await self.account.post(url=self.url, payload={"status": str(AuthorizationStatus.AUTHORIZATION_DEACTIVATED)})
        await self.update_fields(resp)

    #TODO translate challanges from json to objects


class ACME_Authorizations(ElementList[ACME_Authorization]):
    pass
