import pytest
import sys
from pathlib import Path
from subprocess import run

SERVER_TERMINAL = Path("/tmp/server_terminal")
ERROR_TERMINAL = Path("/tmp/error_terminal")


def get_error_tty() -> Path | None:
    try:
        with open(ERROR_TERMINAL, "r") as f:
            s = f.readline()[:-1]
            return Path(s)
    except IOError as e:
        print(e, file=sys.stderr)
        return None


@pytest.fixture
def get_server_tty() -> Path | None:
    if SERVER_TERMINAL.exists():
        try:
            with open(SERVER_TERMINAL, "r") as f:
                s = f.readline()[:-1]
                return Path(s)
        except IOError as e:
            print(e, file=sys.stderr)
    return None
