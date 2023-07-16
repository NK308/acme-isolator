from .base import ACME_Object
from dataclasses import dataclass, InitVar, fields, field
from aiohttp import request
from ..request.constants import USER_AGENT


@dataclass(order=False, kw_only=True)
class ACME_Directory(ACME_Object):
    newNonce: str
    newAccount: str
    newOrder: str
    revokeCert: str
    keyChange: str
    meta: InitVar[dict]
    website: str = field(default="")
    newAuthz: str = None
    parent: ACME_Object | None = field(default=None)

    def __post_init__(self, meta):
        self.website = meta["website"]

    def __iter__(self):
        return iter({k: v for (k, v) in self.__dict__.items() if k in {"newNonce", "newAccount", "newOrder", "newAuthz", "revokeCert", "keyChange"}}.items())

    @classmethod
    async def get_directory(cls, url: str):
        async with request("GET", url, headers={"User-Agent": USER_AGENT}) as resp:
            resp.raise_for_status()
            j = await resp.json(encoding="utf-8")
            class_fields = {f.name for f in fields(cls)}
            return cls(url=url, **{k: v for k, v in j.items() if k in class_fields or k == "meta"})


