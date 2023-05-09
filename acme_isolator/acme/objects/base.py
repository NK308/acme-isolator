import json
from abc import ABC
from dataclasses import dataclass, fields


@dataclass(order=False, kw_only=True)
class ACME_Object(ABC):

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
