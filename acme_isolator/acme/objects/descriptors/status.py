from enum import Enum as Status


class StatusDescriptor:
    def __init__(self, enumType: type, name = "status"):
        self.type = enumType
        self.name = "status"

    def __set__(self, instance, value):
        if type(value) is str:
            instance.__dict__[self.name] = self.type(value)
        elif type(value) is self.type:
            instance.__dict__[self.name] = value
        else:
            raise ValueError(f"Type {type(value).__name__} not supported for field {self.name}.")

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]
