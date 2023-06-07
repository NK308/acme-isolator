from .base import ACME_Object
from .identifier import ACME_Identifier
from .authorization import ACME_Authorization
from dataclasses import dataclass, field, InitVar
from collections.abc import Sequence
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

    def __post_init__(self, identifiers: dict):
        self.identifier = [ACME_Identifier.parse(identifier) for identifier in identifiers]

    async def update(self):
        data, status = await self.parent.parent.request(self.url, None)
        if status == 200:
            for key, value in data.items():

    @classmethod
    async def get_from_url(cls, order_list: "ACME_Orders", url: str):
        data, status = await order_list.parent.request(url, None)
        if status == 200:
            return ACME_Order(url=url, parent=order_list, **data)
        else:
            raise ConnectionError(f"Server returned status code {status} while fetching order from {url}.")


@dataclass(order=False, kw_only=True)
class ACME_Orders(ACME_Object, Sequence):
    orders: list[str | ACME_Order]

    def __getitem__(self, i):
        return self.orders[i]

    def __len__(self):
        return len(self.orders)

    def __iter__(self):
        return self.orders.__iter__()

    async def update_list(self):
        data, status = await self.parent.request(self.url, None)
        if status == 200:
            new_list = data["orders"]
            for entry in new_list:  # Add new orders to list
                if entry in self.orders:
                    pass
                elif entry in list(map(lambda order: order.url, filter(lambda obj: type(obj) == ACME_Order, self.orders))):
                    pass
                else:
                    self.orders.append(entry)

            for order in self.orders:  # Remove missing orders from list
                if type(order) == str:
                    if order in new_list:
                        continue
                elif type(order) == ACME_Order:
                    if order.url in new_list:
                        continue
                self.orders.remove(order)
        else:
            raise ConnectionError(f"Server returned status code {status} while fetching orders from {self.url}.")

    async def update_orders(self):
        new_objects = gather(*[ACME_Order.get_from_url(self, url) for url in self.orders if type(url) == str])
        updates = gather(*[order.update() for order in self.orders if type(order) == ACME_Order])
        self.orders.extend((await gather(new_objects, updates))[0])

