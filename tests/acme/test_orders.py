import pytest
import pytest_asyncio

from acme_isolator.acme.objects.account import ACME_Account
from acme_isolator.acme.objects.order import ACME_Orders, ACME_Order, ACME_Identifier


class TestOrderCreation:

    @pytest.mark.pebble
    @pytest.mark.asyncio
    async def test_order_list(self, pebble_session):
        assert type(pebble_session.orders) == ACME_Orders.url_class
        pebble_session.orders = await pebble_session.orders.request_object(parent=pebble_session)
        assert type(pebble_session.orders) == ACME_Orders
