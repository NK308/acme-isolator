import json
from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass, fields, field, InitVar
from typing import Self, Union, TypeVar, ClassVar, Generic, get_args, Coroutine
from asyncio import gather, Lock

AcmeUrl = TypeVar("AcmeUrl", bound="AcmeUrlBase")
AcmeObject = TypeVar("AcmeObject", bound="ACME_Object")
AcmeElement = TypeVar("AcmeElement", bound="ACME_Object")
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
    def account(self) -> ACME_Account:
        return self.parent.account

    @staticmethod
    def complete_dict(response_url: str, parent: AcmeObject | None = None, **additional_fields) -> dict:
        return dict(parent=parent, url=response_url)

    convert_table: ClassVar[dict]

    @classmethod
    def convert_dict(cls, d: dict) -> dict:
        for key in cls.convert_table.keys():
            if key in d.keys():
                if isinstance(d[key], str):
                    d[key] = cls.convert_table[key](d[key])
                elif isinstance(d[key], list):
                    new_list = list()
                    for s in d[key]:
                        if isinstance(s, str):
                            new_list.append(cls.convert_table[key](s))
                        else:
                            new_list.append(s)
                    d[key] = new_list
        return d

    @classmethod
    async def get_from_url(cls, parent_object: AcmeObject, url: str, **additional_fields) -> Self:
        data, status, location = await parent_object.account.post(url=url, payload=None)
        assert status == cls.request_return_code
        data = cls.convert_dict(data)
        data.update(cls.complete_dict(parent=parent_object, response_url=url, **additional_fields))
        return cls(**data)

    hold_keys: ClassVar[set] = {"parent"}  # Set of keys, not to be updated by generic update method

    def update_fields(self, data: dict):
        field_keys = {field.name for field in fields(self)} & set(data.keys()) - self.__class__.hold_keys
        self.__dict__.update({k: v for k, v in data.items() if k in field_keys})

    async def get_update(self):
        data, status, location = await self.account.post(url=self.url, payload=None)
        assert status == 200
        self.update_fields(data)


@dataclass(order=False, kw_only=True)
class ElementList(Generic[AcmeElement], Sequence, ABC):
    _list: list[AcmeObject | AcmeUrl] = field(init=False, default_factory=list)
    parent: AcmeObject

    objects: InitVar[list]
    list_lock: Lock = field(init=False, default_factory=Lock)
    content_type: ClassVar[type(AcmeObject)]

    # convert_table: ClassVar[dict]

    def __init_subclass__(cls, **kwargs):
        cls.content_type = get_args(cls.__orig_bases__[0])

    def __post_init__(self, objects: list):
        for element in objects:
            if element is str:
                self._list.append(self.content_type.url_class(element))
            elif element is dict:
                self._list.append(self.content_type(parent=self.parent, **element))
            else:
                raise TypeError(f"List contains element of type {type(element)}")

    def _get_parent(self) -> AcmeObject:
        return self.parent

    async def request_element(self, element: AcmeUrl) -> AcmeElement:
        return await element.outer_class.get_from_url(parent_object=self._get_parent(), url=element)

    async def request_all_elements(self):
        with self.list_lock:
            temp_list = list()
            todo: list[Coroutine] = list()
            for element in self._list:
                if isinstance(element, ACME_Object):
                    temp_list.append(element)
                elif isinstance(element, AcmeUrlBase):
                    todo.append(self.request_element(element))
            new_elements = await gather(*todo)
            self._list = temp_list + new_elements

    async def update_all_elements(self):
        with self.list_lock:
            raise NotImplementedError  # TODO implement

    def __getitem__(self, i):
        return self._list[i]

    def __len__(self):
        return len(self._list)

    def __iter__(self):
        return self._list.__iter__()


@dataclass(order=False, kw_only=True)
class ACME_List(Generic[AcmeElement], ACME_Object, ElementList[AcmeElement], ABC):
    def _get_parent(self) -> AcmeObject:
        return self
