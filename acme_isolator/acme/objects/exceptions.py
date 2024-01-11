import json


class ACME_Exception(Exception):
    pass


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

