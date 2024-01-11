import sys

import pytest
import pytest_asyncio

from acme_isolator.acme.objects.account import ACME_Account
from jwcrypto.jwk import JWK


@pytest.mark.pebble
@pytest.mark.asyncio
async def test_account_creation(pebble_session_without_account, generate_key_pair):
    account = await ACME_Account.create_from_key(session=pebble_session_without_account, key=generate_key_pair, contact=["mailto:notmymail@example.com"])


@pytest.mark.asyncio
async def test_account_fetching(pebble_session, pebble_session_without_account):
    await ACME_Account.get_from_key(session=pebble_session_without_account, key=pebble_session.key)
