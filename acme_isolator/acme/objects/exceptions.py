import json


class ACME_Exception(Exception):
    pass

class ACME_ProblemException(ACME_Exception):
    type: str = "urn:ietf:params:acme:error"
    description: str | None
    detail: str
    identifier = None
    subproblems: list

    def __init__(self, type: str, detail: str):
        self.type = type
        self.detail = detail

    @staticmethod
    def parse_problem(data: dict):
        pass


class MalformedException(ACME_Exception):



class UnexpectedResponseException(ACME_Exception):
    response = dict | None

    def __init__(self, code, response: dict | None = None, msg: str | None = None):
        self.code = code
        if response is not None:
            self.response = response
        msg_prefix = f"Unexpected Response (status: {code})"
        if msg is None and response is not None:
            msg = f"{msg_prefix}: {json.dumps(response)}"
        elif msg is not None:
            msg = f"{msg_prefix}: {msg}"
        super(Exception, self).__init__(msg)

    def convert_exception(self) -> ACME_Exception:
        return self  # TODO interpret response and return a more specific exception

