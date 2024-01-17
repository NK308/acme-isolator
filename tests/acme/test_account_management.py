import sys

import pytest
import pytest_asyncio

from acme_isolator.acme.objects.account import ACME_Account
from acme_isolator.acme.objects.exceptions import AccountDoesNotExistException
from jwcrypto.jwk import JWK


class TestAccount:

    @pytest.mark.pebble
    @pytest.mark.asyncio
    async def test_account_creation(self, pebble_session_without_account, generate_key_pair):
        account = await ACME_Account.create_from_key(session=pebble_session_without_account, key=generate_key_pair[0], contact=["mailto:notmymail@example.com"])


    @pytest.mark.asyncio
    async def test_account_fetching(self, pebble_session, pebble_session_without_account):
        await ACME_Account.get_from_key(session=pebble_session_without_account, key=pebble_session.key)

    @pytest.mark.asyncio
    async def test_nonexisting_account(self, pebble_session_without_account, generate_key_pair):
        try:
            await ACME_Account.get_from_key(session=pebble_session_without_account, key=generate_key_pair[0])
        except AccountDoesNotExistException:
            pass
        except Exception as e:
            raise AssertionError(f"Got {e.__class__} instead of AccountDoesNotExistException") from e
        else:
            raise AssertionError("Expected an AccountDoesNotExistException, but got none.")

    @pytest.mark.asyncio
    @pytest.mark.key_count(2)
    async def test_key_rollover(self, pebble_session, generate_key_pair):
        await pebble_session.key_rollover(new_key=generate_key_pair[1])
        try:
            await ACME_Account.get_from_key(key=generate_key_pair[0], session=pebble_session.session)
        except AccountDoesNotExistException:
            pass
        else:
            raise AssertionError("Old key is still accepted by the server")
        ACME_Account.get_from_key(key=generate_key_pair[1], session=pebble_session.session)


