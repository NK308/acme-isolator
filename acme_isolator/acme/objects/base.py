import json
from abc import ABC
from dataclasses import dataclass, fields
from typing import Self, Union, TypeVar, ClassVar

from ..request.jws import JwsKid

AcmeUrl = TypeVar("AcmeUrl", bound="AcmeUrlBase")
AcmeObject = TypeVar("AcmeObject", bound="ACME_Object")
ACME_Account = TypeVar("ACME_Account", bound="ACME_Object")


class AcmeUrlBase(str, ABC):
    outer_class: ClassVar[type(AcmeObject)]

    async def request_object(self, parent: AcmeObject) -> AcmeObject:  #TODO more specific type hinting
        return self.outer_class.get_from_url(parent_object=parent, url=str(self))


@dataclass(order=False, kw_only=True)
class ACME_Object(ABC):
    url: str
    parent: Union["ACME_Object", None]

    url_class: ClassVar[type(AcmeUrl)]
    request_return_code: ClassVar[int] = 200

    def __init_subclass__(cls, **kwargs):
        cls.url_class = type(f"{cls.__name__}Url", (AcmeUrlBase,), dict(outer_class=cls))

    @property
    def account(self):
        return self.parent.account()

    @classmethod
    async def get_from_url(cls, parent_object: "ACME_Object", url: str) -> Self:
        data, status = await parent_object.account.request(url, None)
        if status == 200 or status == 201:
            return cls(url=url, parent=parent_object, **data)
        else:
            raise ConnectionError(f"Server returned status code {status} while fetching {cls.__name__} from {url}.")

    def update_list(self, field_list: list[str | Self], update_list: list[str]) -> list[str | Self]:
        for e in update_list:
            if e in field_list:
                continue
            elif e not in [acme.url for acme in field_list if not type(acme) == str]:
                field_list.append(e)
        for e in field_list:
                if type(e) == str and e in update_list:
                    continue
                elif type(e) == str and e not in update_list:
                    field_list.remove(e)
                elif e.url not in update_list:
                    field_list.remove(e)
        return field_list

