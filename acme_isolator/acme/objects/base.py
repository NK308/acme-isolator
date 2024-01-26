import json
from types import UnionType, NoneType
from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass, fields, field, InitVar, Field
from typing import Self, Union, TypeVar, ClassVar, Generic, get_origin, get_args, Coroutine, Any, Optional
from asyncio import gather, Lock

AcmeUrl = TypeVar("AcmeUrl", bound="AcmeUrlBase")
AcmeObject = TypeVar("AcmeObject", bound="ACME_Object")
AcmeElement = TypeVar("AcmeElement", bound="ACME_Object")
ACME_Account = TypeVar("ACME_Account", bound="ACME_Object")


class AcmeUrlBase(str, ABC):
    outer_class: ClassVar[type(AcmeObject)]

    async def request_object(self, parent: AcmeObject) -> AcmeObject:  #TODO more specific type hinting
        return await self.outer_class.get_from_url(parent_object=parent, url=str(self))


@dataclass(order=False, kw_only=True)
class ACME_Object(ABC):
    url: str
    parent: Union["ACME_Object", None]

    url_class: ClassVar[type(AcmeUrl)]
    hold_keys: ClassVar[set] = {"parent", "url"}  # Set of keys, not to be updated by generic update method
    request_return_code: ClassVar[int] = 200

    def __init_subclass__(cls, **kwargs):
        cls.url_class = type(f"{cls.__name__}Url", (AcmeUrlBase,), dict(outer_class=cls))

    @property
    def account(self) -> ACME_Account:
        return self.parent.account

    @staticmethod
    def check_acme_union(t) -> tuple[bool, type | None]:  # check, if type variable describes a version of ACME_Object | AcmeUrl
        if get_origin(t) is Union:
            l = get_args(t)
            if len(l) == 2:
                if any([issubclass(e, ACME_Object) for e in l]) and any([issubclass(e, AcmeUrlBase) for e in l]):
                    if issubclass(l[0], ACME_Object):
                        c = l[1]
                    else:
                        c = l[0]
                    return True, c
        return False, None

    @staticmethod
    def check_optional_type(t):
        if get_origin(t) is UnionType:
            l = get_args(t)
            if NoneType in l and len(l) == 2:
                if l[0] is None:
                    return l[1]
                else:
                    return l[0]
            elif None in l and len(l) != 2:
                raise NotImplementedError("Union of None and >1 other types not handled")
            else:
                return l
        elif get_origin(t) is Optional:
            return get_args(t)[0]
        else:
            return t

    def update_field(self, f: Field, d: Any):
        key = f.name
        if key in self.hold_keys:
            return
        t = self.check_optional_type(f.type)
        v:f.type = self.__dict__.get(key, None)
        u, i = self.check_acme_union(t)
        if type(d) is str and t is str:
            # field should be a plain string
            self.__dict__[key] = d
        elif u and type(d) is str:
            if isinstance(v, ACME_Object):
                # field already contains acme object and its url matches the string
                assert v.url == d
            else:
                # field should ACME object/url not yet a requested object and str is given and transformed into url object
                self.__dict__[key] = i(d)
        elif type(t) is type:
            if issubclass(t, ElementList):
                if v is None:
                    # object seems to be in __post_init__ generate new ElementList
                    pass  # TODO
                else:
                    # ElementList should be updated with list of dicts
                    pass  # TODO
            else:
                self.__dict__[key] = t(d)
        else:
            self.__dict__[key] = d

    def __post_init__(self, *args, **kwargs):
        self.update_fields(kwargs)

    def update_fields(self, data: dict):
        for key in data.keys():
            for f in fields(self):
                if f.name == key:
                    self.update_field(f, data[key])
                    break

    @classmethod
    async def get_from_url(cls, parent_object: AcmeObject, url: str, **additional_fields) -> Self:
        data, status, location = await parent_object.account.post(url=url, payload=None)
        assert status == cls.request_return_code
        data.update({"parent":parent_object, "response_url":url})
        data.update(additional_fields)
        return cls(**data)

    async def get_update(self):  # TODO maybe adding an recursive option probably has to be combined with lock
        data, status, location = await self.account.post(url=self.url, payload=None)
        assert status == 200
        self.update_fields(data)


@dataclass(order=False, kw_only=True)
class ElementList(Generic[AcmeElement], Sequence, ABC):
    _list: list[AcmeElement | AcmeUrl] = field(init=False, default_factory=list)
    parent: AcmeObject

    # objects: InitVar[list] = field(kw_only=False, init=True)
    list_lock: Lock = field(init=False, default_factory=Lock)
    content_type: ClassVar[type(AcmeObject)]

    convert_table: ClassVar[dict] = dict()

    def __init_subclass__(cls, **kwargs):
        cls.content_type = get_args(cls.__orig_bases__[0])

    def __post_init__(self, *args, **kwargs):
        keys = set(self.convert_table.keys()) & set(kwargs.keys())
        for key in keys:
            for element in kwargs[key]:
                if element is str:
                    self._list.append(self.content_type.url_class(element))
                elif element is dict:
                    self._list.append(self.content_type(parent=self.parent, **element))
                else:
                    raise TypeError(f"List contains element of type {type(element)}")
        for arg in args:
            if arg is str:
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
            self._list = temp_list + list(new_elements)

    async def update_all_elements(self):
        with self.list_lock:
            tasks: list[Coroutine] = list()
            for element in self._list:
                if isinstance(element, ACME_Object):
                    tasks.append(element.get_update())
            await gather(*tasks)

    def __getitem__(self, i):
        return self._list[i]

    def __len__(self):
        return len(self._list)

    def __iter__(self):
        return self._list.__iter__()


@dataclass(order=False, kw_only=True)
class ACME_List(Generic[AcmeElement], ACME_Object, ElementList[AcmeElement], ABC):
    hold_keys: ClassVar[set] = ACME_Object.hold_keys | {"list", "list_lock"}

    def _get_parent(self) -> AcmeObject:
        return self

    async def get_update(self):
        await self.update_all_elements()
