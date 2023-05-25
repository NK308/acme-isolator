from .base import ACME_Object
from dataclasses import dataclass, InitVar, field
from aiohttp import request
from ..request.constants import USER_AGENT


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

    def __iter__(self):
        return {k: v for (k,v) in self.__dict__ if k in {"newNonce", "newAccount", "newOrder", "newAuthz", "revoceCert", "keyChange"}}

    @classmethod
    async def get_directory(cls, directory_url: str):
        async with request("GET", directory_url, headers={"User-Agent": USER_AGENT}) as resp:
            resp.raise_for_status()
            j = await resp.json(encoding="utf-8")
            return cls(**j)


