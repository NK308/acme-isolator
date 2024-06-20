from .base import ACME_Object
from .exceptions import ACME_ProblemException, UnexpectedResponseException, ACME_Exception
from dataclasses import dataclass, InitVar, fields, field
from aiohttp import request
from ..request.constants import USER_AGENT


@dataclass(order=False, kw_only=True)
class ACME_Directory(ACME_Object):
    """
    Representation of a directory resource, as defined in RFC 8555 section 7.1.1.
    This class doesn't do much, besides containing URLs.
    """
    newNonce: str
    newAccount: str
    newOrder: str
    revokeCert: str
    keyChange: str
    meta: InitVar[dict | None]
    website: str = field(default="")
    newAuthz: str = None
    parent: ACME_Object | None = field(default=None)

    def __post_init__(self, meta):
        if meta is not None and "website" in meta:
            self.website = meta["website"]

    def __iter__(self):
        return iter({k: v for (k, v) in self.__dict__.items() if k in {"newNonce", "newAccount", "newOrder", "newAuthz", "revokeCert", "keyChange"} and v is not None}.items())

    @classmethod
    async def get_directory(cls, url: str):
        """
        Factory for fetching a directory resource and creating an `ACME_Directory` from it.
        This subclass of `ACME_Object` has it's own implementation of a factory, since it doesn't have to be related to an account.
        :param url: URL of the directory resource to fetch
        :ptype url: str
        :return: Object created from the server's response.
        :rtype: ACME_Directory
        """
        async with request("GET", url, headers={"User-Agent": USER_AGENT}) as resp:
            j = await resp.json(encoding="utf-8")
            if not resp.status == 200:
                raise UnexpectedResponseException(resp.status, response=await resp.json(encoding="utf-8"), msg="Error while getting directory data").convert_exception()
            class_fields = {f.name for f in fields(cls)}
            return cls(url=url, **{k: v for k, v in j.items() if k in class_fields or k == "meta"})


