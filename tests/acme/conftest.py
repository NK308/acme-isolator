import pytest

import json
from base64 import urlsafe_b64encode
from random import randint
from .terminal_redirection_fixtures import *
from .server_mocking import *
from .key_generation import generate_key_pair
from .staging_fixtures import *
from .pebble_fixtures import *


@pytest.fixture()
def random_nonce():
    return urlsafe_b64encode(bytes([randint(0, 255) for i in range(10)])).decode("ascii").strip("=")


@pytest.fixture()
def random_payload():
    return {"a": [randint(0, 255) for i in range(randint(2, 20))], "b": "test"}


@pytest.fixture()
def random_payload_str(random_payload):
    return json.dumps(random_payload).encode("utf-8")
