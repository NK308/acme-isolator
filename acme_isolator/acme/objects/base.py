import json
from abc import ABC
from dataclasses import dataclass


class ACME_Object(ABC):

    @classmethod
    def __make_object(cls, response: dict):
       return cls(**response)

    @classmethod
    def parse(cls, response: str):
        return json.loads(response, object_hook=cls.__make_object)
