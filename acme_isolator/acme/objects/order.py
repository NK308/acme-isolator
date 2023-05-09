from .base import ACME_Object
from .identifier import ACME_Identifier
from .authorization import ACME_Authorization
from dataclasses import dataclass, field, InitVar


@dataclass(order=False, kw_only=True)
class ACME_Order(ACME_Object):
    status: str
    expires: str
    identifier: ACME_Identifier = field(init=False)
    identifier: InitVar[dict]
    notBefore: str|None
    notAfter: str|None
    error: dict|None
    authorizations: list[str]|list[ACME_Authorization]
    finalize: str
    certificate: str|None

    def __post_init__(self, identifier: dict):
        self.identifier = ACME_Identifier.parse(identifier)