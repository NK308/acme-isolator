from .base import ACME_Object, ClassVar
from .exceptions import ACME_ProblemException
from .descriptors import Status, StatusDescriptor
from abc import ABC
from dataclasses import dataclass, field


class ChallengeStatus(Status):
    CHALLENGE_PENDING = "pending"
    CHALLENGE_PROCESSING = "processing"
    CHALLENGE_VALID = "valid"
    CHALLENGE_INVALID = "invalid"


class ErrorDescriptor:
    def __get__(self, instance, owner):
        return instance.__dict__["error"]

    def __set__(self, instance, value):
        e = ACME_ProblemException.parse_problem(value)
        if e is None:
            e = value
        instance.__dict__["error"] = e


@dataclass(kw_only=True)
class ACME_Challenge(ACME_Object):
    type: str
    status: ChallengeStatus = field(default=StatusDescriptor(ChallengeStatus))
    validated: None | str
    error: ACME_ProblemException | dict = field(default=ErrorDescriptor())
    # For now this is just a stub
    #TODO add concrete implementation for dns challenge

    def keyAuthorization(self) -> str:
        #TODO implement rfc7638
        pass


class ACME_Challenge_dns_01(ACME_Challenge):
    token: str
    type: str = "dns-01"
    type: ClassVar[str] = "dns-01"


type: str = "dns-01"
