from ..base import ACME_Object, ElementList


class AcmeDescriptor:
    """
    Descriptor for `ACME_Object` and it's subclasses, to make it easy to define fields, which can either be assigned an instance of a specific `ACME_Object` subclass or alternatively it's corresponding `AcmeUrl` class, or an URL in form of a simple `str`, which is then automatically converted to the URL class.
    """
    def __init__(self, subclass: type):
        if issubclass(subclass, ACME_Object):
            self.type = subclass
        else:
            raise ValueError("Type has to be a subclass of ACME_Object")

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, insttype = None):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if value is self:
            raise ValueError(f"Field {self.name} has not been provided to __init__ of {self.type}.")
        if isinstance(instance.__dict__.get(self.name, None), self.type):
            if isinstance(value, str):
                if not instance.__dict__[self.name].url == str(value):
                    raise NotImplementedError(f"URL from object has changed from {instance.__dict__[self.name].url} to {value}.")  # TODO maybe handle change of acme object after update from server
            elif type(value) is self.type:
                if not instance.__dict__[self.name].url == value.url:
                    raise NotImplementedError(f"URL from object has changed from {instance.__dict__[self.name].url} to {value.url}.")  # TODO maybe handle change of acme object after update from server
            else:
                raise ValueError(f"Field can only take vales of the types str | {self.type.__name__} | {self.type.url_class.__name__}")
        else:
            if type(value) is str:
                instance.__dict__[self.name] = self.type.url_class(value)
            elif type(value) is self.type.url_class or type(value) is self.type:
                instance.__dict__[self.name] = value
            else:
                raise ValueError(f"Field can only take vales of the types str | {self.type.__name__} | {self.type.url_class.__name__} and not of type {type(value).__name__}.")


class ListDescriptor:
    def __init__(self, subclass: type):
        if issubclass(subclass, ElementList):
            self.listSubclass = subclass
        else:
            raise ValueError("Type has to be a subclass of ElementList")

    def __get__(self, instance, owner):
        if self.name in instance.__dict__.keys():
            l = instance.__dict__[self.name]
        else:
            l = self.listSubclass([], parent=instance)
            instance.__dict__[self.name] = l
            return l

    def __set__(self, instance, value):
        if self.name not in instance.__dict__.keys():
            if type(value) is self.listSubclass:
                instance.__dict__[self.name] = value
            elif type(value) is list:
                print(self.listSubclass, type(value), type(instance))
                instance.__dict__[self.name] = self.listSubclass(value, instance)
        else:
            raise NotImplementedError  # TODO has this to be implemented or should it be an error?

    def __set_name__(self, owner, name):
        self.name = name
