from .base import ACME_Object
from dataclasses import dataclass, InitVar, field


@dataclass(order=False, kw_only=True)
class ACME_Directory(ACME_Object):
    newNonce: str
    newAccount: str
    newOrder: str
    newAuthz: str
    revoceCert: str
    keyChange: str
    website: str
    meta: InitVar[dict]

    def __post_init__(self, meta):
        self.website = meta["website"]

