from abc import ABC
from collections.abc import MutableSet
from dataclasses import dataclass, fields, field, InitVar
from typing import Self, Union, TypeVar, ClassVar, Generic, get_args, Coroutine
from asyncio import gather, Lock

AcmeUrl = TypeVar("AcmeUrl", bound="AcmeUrlBase")
AcmeObject = TypeVar("AcmeObject", bound="ACME_Object")
AcmeElement = TypeVar("AcmeElement", bound="ACME_Object")
ACME_Account = TypeVar("ACME_Account", bound="ACME_Object")


class AcmeUrlBase(str, ABC):
    outer_class: ClassVar[type(AcmeObject)]

    async def request_object(self, parent: AcmeObject) -> AcmeObject:
        return await self.outer_class.get_from_url(parent_object=parent, url=str(self))


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
    @classmethod
    async def get_from_url(cls, parent_object: AcmeObject, url: str, **additional_fields) -> Self:
        data, status, location = await parent_object.account.post(url=url, payload=None)
        assert status == cls.request_return_code
        data.update({"parent": parent_object, "url": url})
        return cls(**data)

    hold_keys: ClassVar[set] = {"parent"}  # Set of keys, not to be updated by generic update method

    def update_fields(self, data: dict):
        keys = {f.name for f in fields(self)} & set(data.keys()) - self.__class__.hold_keys
        for key in keys:
            if key in self.__class__.__dict__.keys():
                self.__class__.__dict__[key].__set__(self, data[key])
            else:
                self.__dict__[key] = data[key]

    async def get_update(self):  # TODO maybe adding an recursive option probably has to be combined with lock
        data, status, location = await self.account.post(url=self.url, payload=None)
        assert status == 200
    #    ** kwargs       self.update_fields(data)


@dataclass(order=False, kw_only=False)
class ElementList(Generic[AcmeElement], MutableSet, ABC):
    items: InitVar[list[AcmeElement | AcmeUrl | str] | None]
    _list: list[AcmeElement | AcmeUrl] = field(init=False, default_factory=list)
    parent: AcmeObject = field(kw_only=True)

    list_lock: Lock = field(init=False, default_factory=Lock)
    content_type: ClassVar[type(AcmeObject)]

    def __init_subclass__(cls, **kwargs):
        cls.content_type = get_args(cls.__orig_bases__[0])[0]

    def __post_init__(self, items: list):
        for element in items:
            self.add(element)

    def __find_element(self, value) -> int | None:
        if type(value) is self.content_type:
            url = value.url
        elif type(value) is self.content_type.url_class:
            url = str(value)
        else:
            return None
        for i in range(len(self._list)):
            e = self._list[i]
            if type(e) is self.content_type and url == e.url:
                return i
            elif type(e) is self.content_type.url_class and url == str(e):
                return i
        return None


    def __contains__(self, item):
        return self.__find_element(item) is not None

    def __iter__(self):
        self._list.__iter__()

    def __len__(self):
        return len(self._list)

    def add(self, value):
        if value not in self:
            if type(value) is self.content_type or value in self and type(value) is self.content_type:
                self._list.append(value)
            elif type(value) is str:
                self._list.append(self.content_type.url_class(value))
            else:
                raise ValueError(f"Class {self.__class__.__name__} does no accept objects of type {type(value)}")
        elif type(value) is self.content_type:
            i = self.__find_element(value)
            if type(self._list[i]) is self.content_type.url_class:
                del self._list[i]
                self._list.append(value)
            else:
                raise NotImplementedError("Total replacement of complete ACME_Object not implemented")
        elif type(value) is self.content_type.url_class | str:
            pass
        else:
            raise ValueError(f"Class {self.__class__.__name__} does no accept objects of type {type(value)}")

    def remove(self, value):
        e = self.__find_element(value)
        if e is not None:
            del self._list[e]
        else:
            raise KeyError(f"Key with url representation {value.url if type(value) is self.content_type else str(value)} does not exist.")

    def discard(self, value):
        try:
            self.remove(value)
        except KeyError:
            pass

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
            self._list = temp_list + list(new_elements)

    async def update_all_elements(self):
        with self.list_lock:
            tasks: list[Coroutine] = list()
            for element in self._list:
                if isinstance(element, ACME_Object):
                    tasks.append(element.get_update())
            await gather(*tasks)
