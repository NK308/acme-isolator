from .base import ACME_Object, ACME_List, ClassVar
from .identifier import ACME_Identifier
from .authorization import ACME_Authorization
from dataclasses import dataclass, field, InitVar
from asyncio import gather, create_task


@dataclass(order=False, kw_only=True)
class ACME_Order(ACME_Object):
    status: str
    expires: str
    identifiers: list[ACME_Identifier] = field(init=False)
    identifiers: InitVar[list[dict]]
    notBefore: str | None
    notAfter: str | None
    error: dict | None
    authorizations: list[str] | list[ACME_Authorization]
    finalize: str
    certificate: str | None

    def __post_init__(self, identifiers: list[dict]):
        self.identifier = [ACME_Identifier.parse(identifier) for identifier in identifiers]

    async def update(self):  # TODO rewrite/remove
        data, status = await self.parent.parent.request(self.url, None)
        if status == 200:
            for key, value in data.items():
                if key == "status":
                    self.status = value
                elif key == "finalize":
                    self.finalize = value
                elif key == "certificate":
                    self.certificate = value


@dataclass
class ACME_Orders(ACME_List[ACME_Order]):
    convert_table: ClassVar[dict] = {"orders": ACME_Order}

    orders: InitVar[list[dict]]
    # TODO add method for creating new orders
