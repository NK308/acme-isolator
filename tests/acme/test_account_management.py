import sys

import pytest
import pytest_asyncio

from acme_isolator.acme.objects.account import ACME_Account
from jwcrypto.jwk import JWK


@pytest.mark.pebble
@pytest.mark.asyncio
async def test_account_creation(pebble_session_without_account):
    key: JWK = JWK.generate(kty="EC", size=265)
    account = await ACME_Account.create_from_key(session=pebble_session_without_account, key=key, contact=["mailto:notmymail@example.com"])


