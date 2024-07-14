import pytest
import pytest_asyncio

from acme_isolator.acme.objects.base import AcmeUrlBase, ElementList
from acme_isolator.acme.objects.account import ACME_Account
from acme_isolator.acme.objects.order import ACME_Orders, ACME_Order
from acme_isolator.acme.objects.identifier import ACME_Identifier_DNS


class TestOrderCreation:

    @pytest.mark.pebble
    @pytest.mark.asyncio
    async def test_order_list(self, pebble_session):
        assert type(pebble_session.orders) is ACME_Orders.url_class
        pebble_session.orders = await pebble_session.orders.request_object(parent=pebble_session)
        assert type(pebble_session.orders) is ACME_Orders

    @pytest.mark.pebble
    @pytest.mark.asyncio
    async def test_order_creation_single_domain(self, pebble_session):
        pebble_session.orders = await pebble_session.orders.request_object(parent=pebble_session)
        identifiers = [ACME_Identifier_DNS(value="not-my.domain.com")]
        order = await pebble_session.orders.create_order(identifiers=identifiers)
        assert type(order) is ACME_Order

    @pytest.mark.pebble
    @pytest.mark.asyncio
    async def test_order_creation_multi_domain(self, pebble_session):
        pebble_session.orders = await pebble_session.orders.request_object(parent=pebble_session)
        identifiers = [ACME_Identifier_DNS(value="not-my.domain.com"),
                       ACME_Identifier_DNS(value="subdomain-of.not-my.domain.com"),
                       ACME_Identifier_DNS(value="also-not.my-domain.com")]
        order = await pebble_session.orders.create_order(identifiers=identifiers)
        assert type(order) is ACME_Order

    @pytest.mark.pebble
    @pytest.mark.asyncio
    async def test_list_access(self, pebble_session):
        pebble_session.orders = await pebble_session.orders.request_object(parent=pebble_session)
        identifiers = [ACME_Identifier_DNS(value="not-my.domain.com")]
        orders = pebble_session.orders
        order = await orders.create_order(identifiers=identifiers)
        assert isinstance(orders, ACME_Orders)
        assert len(orders) == 1
        assert type(orders._list) == list
        for order in orders:
            assert type(order) == ACME_Order

    @pytest.mark.pebble
    @pytest.mark.asyncio
    async def test_authorization_datatype(self, pebble_session):
        pebble_session.orders = await pebble_session.orders.request_object(parent=pebble_session)
        identifiers = [ACME_Identifier_DNS(value="not-my.domain.com")]
        order = await pebble_session.orders.create_order(identifiers=identifiers)
        assert len(order.authorizations) > 0
        for auth in order.authorizations:
            assert isinstance(auth, AcmeUrlBase)

