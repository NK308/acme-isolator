import pytest
import pytest_asyncio

from acme_isolator.acme.objects.account import ACME_Account
from acme_isolator.acme.objects.order import ACME_Orders, ACME_Order
from acme_isolator.acme.objects.identifier import ACME_Identifier_DNS


class TestOrderCreation:

    @pytest.mark.pebble
    @pytest.mark.asyncio
    async def test_order_list(self, pebble_session):
        assert type(pebble_session.orders) == ACME_Orders.url_class
        pebble_session.orders = await pebble_session.orders.request_object(parent=pebble_session)
        assert type(pebble_session.orders) == ACME_Orders

    @pytest.mark.pebble
    @pytest.mark.asyncio
    async def test_order_creation(self, pebble_session):
        pebble_session.orders = await pebble_session.orders.request_object(parent=pebble_session)
        identifiers = [ACME_Identifier_DNS(value="not-my.domain.com")]
        order = await pebble_session.orders.create_order(identifiers=identifiers)
        assert type(order) == ACME_Order
