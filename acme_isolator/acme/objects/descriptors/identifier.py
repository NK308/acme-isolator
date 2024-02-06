from ..identifier import ACME_Identifier


class IdentifierDescriptor:

    def __set__(self, instance, value):
        if isinstance(value, ACME_Identifier):
            instance.__dict__[self.name] = value
        else:
            instance.__dict__[self.name] = ACME_Identifier.parse(value)
        # else:
        #     raise ValueError(f"Type {type(value).__name__} not supported for field {self.name}.")

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set_name__(self, owner, name):
        self.name = name


class IdentifierListDescriptor:
    def __set__(self, instance, value):
        if isinstance(value, list):
            l = list()
            for e in value:
                if isinstance(e, ACME_Identifier):
                    l.append(e)
                elif isinstance(e, dict):
                    l.append(ACME_Identifier.parse(e))
                else:
                    raise ValueError
            instance.__dict__[self.name] = l
        else:
            raise ValueError

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set_name__(self, owner, name):
        self.name = name
