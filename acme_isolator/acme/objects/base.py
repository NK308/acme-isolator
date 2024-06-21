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

    @property
    def url(self) -> str:
        return str(self)

    async def request_object(self, parent: AcmeObject) -> AcmeObject:
        return await self.outer_class.get_from_url(parent_object=parent, url=str(self))


_object_register: dict[str, AcmeObject] = dict()

@dataclass(order=False, kw_only=True)
class ACME_Object(ABC):
    """
    Base class for objects that represent a resource on the ACME server.
    Can be constructed by requesting the data from the resource URL. Holds a reference to the URL, from which it has been constructed.

    :ivar url: `AcmeUrl` subclass instance of the URL of the resource on the server, which is mirrored by this object.
    :vartype url: AcmeUrl
    :cvar url_class: Class object of the `AcmeUrl` subclass which is related to this (sub)class  of `ACME_Object`.
    :vartype url_class: Class
    :ivar parent: Parent object
    :vartype parent: Acme_Object
    :ivar account: Account, to which this resource belongs.
    :vartype account: ACME_Account
    :cvar request_return_code: By default expected return code when  fetching the current state of the object from the server. Defaults to 200.
    :vartype request_return_code: int
    """
    url: str
    parent: Union["ACME_Object", None]

    url_class: ClassVar[type(AcmeUrl)]
    request_return_code: ClassVar[int] = 200

    hold_keys: ClassVar[set] = {"parent", "url"}  # Set of keys, not to be updated by generic update method

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
        """
        Factory method, to construct a new instance from URL, by sending a request to the server and parsing the response.

        :param parent_object: Parent of the requested object.
        :ptype parent_object: AcmeObject
        :param url: Resouerce URL on the server.
        :param additional_fields:
        :rtype: ACME_Object
        """
        data, status, location = await parent_object.account.post(url=url, payload=None)
        assert status == cls.request_return_code
        data.update({"parent": parent_object, "url": url})
        if url in _object_register:
            o = _object_register[url]
            o.update_fields(data)
        else:
            o = cls(**data)
        return o



    def update_fields(self, data: dict):
        """
        Update the object's fields with data from a dictionary, ommitting entries which are not defined as part of the class.

        :param data: Dictionary with keys having some intersection with the set of fields available to the object.
        :ptype data: dict
        """
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
    """
    Abstract `MutableSet` class to contain objects representing a specific type of resource, able to handle them as `ACME_Object` subclass instances, or their respective URL class.
    While comparing an object to elements from the set, they are compared by their URLs.
    Trying to add a resource that is already contained in the set can "upgrade" the element by replacing it, if the new object is an instance of `ACME_Object`, while the already contained element is an `AcmeUrl`.
    This class also provides methods to iterate though all elements, fetch their updated data from the server and update the elements accordingly.

    :ivar parent: Object, which has to contain this "list" of resources, according to RFC 8555.
    :vartype parent: ACME_Object
    :cvar content_type: Subclass of `ACME_Object`, that represents the resource, which is contained by this class. Set while subclassing `ElementList`
    :vartype content_type: Class
    """
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
        """
        Check, if a object representation of a resource is already in the list, not matter if it is derived from `ACME_Object` or from `AcmeUrl`, by comparing the URLs of the objects.

        :param value: The object of the resource to find in the list.
        :ptype value: `content_type` | `content_type.url_class` | `str`
        :return: Index of the object, found inside of the list, or `None` if it isn't found in the list.
        :rtype: int | None
        """
        if type(value) in [str, self.content_type, self.content_type.url_class]:
            if type(value) is self.content_type:
                url = value.url
            else:
                url = value
            for i in range(len(self._list)):
                e = self._list[i]
                if e.url == url:
                    return i
        else:
            raise TypeError(f"Tried to look for type {type(value)} but only {self.content_type} and {self.content_type.url_class} are allowed.")
        return None


    def __contains__(self, item):
        return self.__find_element(item) is not None

    def __iter__(self):
        self._list.__iter__()

    def __len__(self):
        return len(self._list)

    def add(self, value):
        """
        Add new object to the list. Since this class mostly behaves like a `set`, it can not contain a resource (identified by it's URL) more than once.
        If a resource is already contained represented by it's `AcmeUrl` object, and the new object is the same resoure, but represented as `ACME_Object`, the element in the list gets replaced, but not the other way round.

        :param value: New element to add to the list.
        :ptype value: `content_type` | `content_type.url_class`
        """
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
        """
        Request object from URL and set corerct parent.

        :param element: URL of the requested object
        :ptype element: `content_type.url_class`
        :return: Object generated from the server's response
        :rtype: `content_type`
        """
        return await element.outer_class.get_from_url(parent_object=self._get_parent(), url=element)

    async def request_all_elements(self):
        """
        Request all resources, which are currently only contained as `content_type.url_class`, generate the corresponding `content_type` objects and replace them in the container.
        """
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
        """
        Request all resources, which are contained as `content_type` objects and update them.
        """
        with self.list_lock:
            tasks: list[Coroutine] = list()
            for element in self._list:
                if isinstance(element, ACME_Object):
                    tasks.append(element.get_update())
            await gather(*tasks)
