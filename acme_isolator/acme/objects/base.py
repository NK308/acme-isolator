import json
from abc import ABC
from dataclasses import dataclass, fields
from typing import Self


@dataclass(order=False, kw_only=True)
class ACME_Object(ABC):
    url: str
    parent: "ACME_Object" | None

    @classmethod
    def _make_object(cls, response: dict):
        return cls(**response)

    @classmethod
    def _make_object_with_url_generator(cls, url: str):
        def _make_object_with_url(response: dict):
            return cls(url=url, **response)
        return _make_object_with_url

    @classmethod
    def parse(cls, response: str, url: str|None = None):
        if "url" in [field.name for field in fields(cls)] and url is not None:
            return json.loads(response, object_hook=cls._make_object_with_url_generator(url))
        elif "url" in [field.name for field in fields(cls)] and url is None:
            raise ValueError(f"Class {cls} needs an url.")
        elif "url" not in [field.name for field in fields(cls)] and url is None:
            return json.loads(response, object_hook=cls._make_object)
        else:
            raise ValueError(f"Class {cls} must not have an url.")

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

