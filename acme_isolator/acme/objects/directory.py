import json
from dataclasses import dataclass, InitVar, field


@dataclass(frozen=True, order=False, kw_only=True)
class ACME_Directory:
    newNonce: str
    newAccount: str
    newOrder: str
    newAuthz: str
    revoceCert: str
    keyChange: str
    website: str

    @staticmethod
    def __make_directory(response: dict) -> "ACME_Directory":
        website = response["meta"]["website"]
        del response["meta"]
        return ACME_Directory(website=website, **response)

    @staticmethod
    def decode_directory(response: str) -> "ACME_Directory":
        return json.loads(response, object_hook=ACME_Directory.__make_directory)
