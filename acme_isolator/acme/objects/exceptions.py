import json


class ACME_Exception(Exception):
    pass


_problem_type_registry = dict()

class ACME_ProblemException(ACME_Exception):
    type: str = "urn:ietf:params:acme:error"
    description: str | None
    detail: str
    identifier = None
    subproblems: list | None = None

    def __init__(self, data: dict):
        if self.__class__ == ACME_ProblemException:
            self.type = data.get("type", self.type)
        self.detail = data["detail"]
        self.identifier = data.get("identifier", None)
        super().__init__(self.detail)
        self.add_note(f"problem type: {self.type}")
        self.add_note(self.detail)
        if self.description is not None:
            self.add_note(self.description)
        if self.identifier is not None:
            self.add_note(self.identifier)
        if "subproblems" in data.keys():
            self.subproblems = [ACME_ProblemException(subproblem_data) for subproblem_data in data["subproblems"]]
            self.__cause__ = ExceptionGroup("subproblems", self.subproblems)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.type = f"{ACME_ProblemException.type}:{cls.type}"
        _problem_type_registry[cls.type] = cls

    @staticmethod
    def parse_problem(data: dict):
        try:
            if "type" in _problem_type_registry.keys():
                return _problem_type_registry[type](data)
        except KeyError:
            return ACME_ProblemException(data)
        except AttributeError as e:
            return ExceptionGroup("error while creating ACME_problemException", [e, ACME_ProblemException(data)])
        except Exception as e:
            return e


class AccountDoesNotExistException(ACME_ProblemException):
    type = "accountDoesNotExist"
    description = "The request specified an account that does not exist"


class AlreadyRevokedException(ACME_ProblemException):
    type = "alreadyRevoked"
    description = "The request specified a certificate to be revoked that has already been revoked"


class BadCSRException(ACME_ProblemException):
    type = "badCSR"
    description = "The CSR is unacceptable (e.g., due to a short key)"


class BadNonceException(ACME_ProblemException):
    type = "badNonce"
    description = "The client sent an unacceptable anti-replay nonce"


class BadPublicKeyException(ACME_ProblemException):
    type = "badPublicKey"
    description = "The JWS was signed by a public key the server does not support"


class BadRevocationReasonException(ACME_ProblemException):
    type = "badRevocationReason"
    description = "The revocation reason provided is not allowed by the server"


class BadSignatureAlgorithmException(ACME_ProblemException):
    type = "badSignatureAlgorithm"
    description = "The JWS was signed with an algorithm the server does not support"


class CaaException(ACME_ProblemException):
    type = "caa"
    description = "Certification Authority Authorization (CAA) records forbid the CA from issuing a certificate"


class CompoundException(ACME_ProblemException):
    type = "compound"
    description = "Specific error conditions are indicated in the \"subproblems\" array"


class ConnectionException(ACME_ProblemException):
    type = "connection"
    description = "The server could not connect to validation target"


class DnsException(ACME_ProblemException):
    type = "dns"
    description = "There was a problem with a DNS query during identifier validation"


class ExternalAccountRequiredException(ACME_ProblemException):
    type = "externalAccountRequired"
    description = "The request must include a value for the \"externalAccountBinding\" field"


class IncorrectResponseException(ACME_ProblemException):
    type = "incorrectResponse"
    description = "Response received didn't match the challenge's requirements"


class InvalidContactException(ACME_ProblemException):
    type = "invalidContact"
    description = "A contact URL for an account was invalid"


class MalformedException(ACME_ProblemException):
    type = "malformed"
    description = "The request message was malformed"


class OrderNotReadyException(ACME_ProblemException):
    type = "orderNotReady"
    description = "The request attempted to finalize an order that is not ready to be finalized"


class RateLimitedException(ACME_ProblemException):
    type = "rateLimited"
    description = "The request exceeds a rate limit"


class RejectedIdentifierException(ACME_ProblemException):
    type = "rejectedIdentifier"
    description = "The server will not issue certificates for the identifier"


class ServerInternalException(ACME_ProblemException):
    type = "serverInternal"
    description = "The server experienced an internal error"


class TlsException(ACME_ProblemException):
    type = "tls"
    description = "The server received a TLS error during validation"


class UnauthorizedException(ACME_ProblemException):
    type = "unauthorized"
    description = "The client lacks sufficient authorization"


class UnsupportedContactException(ACME_ProblemException):
    type = "unsupportedContact"
    description = "A contact URL for an account used an unsupported protocol scheme"


class UnsupportedIdentifier(ACME_ProblemException):
    type = "unsupportedIdentifier"
    description = "identifier is of an unsupported type"


class UserActionRequiredException(ACME_ProblemException):
    type = "userActionRequired"
    description = "Visit the \"instance\" URL and take actions specified there"


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

