import pytest

from djmoney.contrib.exchange.backends.base import BaseExchangeBackend
from djmoney.contrib.exchange.models import ExchangeBackend, Rate

from .conftest import ExchangeTest


pytestmark = pytest.mark.django_db


class TestOpenExchangeRates(ExchangeTest):

    def test_get_rates(self):
        assert self.backend.get_rates() == self.expected

    def test_initial_update_rates(self):
        self.backend.update_rates()
        self.assert_rates()

    def test_second_update_rates(self):
        self.backend.update_rates()
        backend = ExchangeBackend.objects.get(name=self.backend.name)
        last_update = backend.last_update
        self.backend.update_rates()
        backend.refresh_from_db()
        assert last_update < backend.last_update


class FixedOneBackend(BaseExchangeBackend):
    name = 'first'

    def get_rates(self, **params):
        return {'EUR': 1}


class FixedTwoBackend(BaseExchangeBackend):
    name = 'second'

    def get_rates(self, **params):
        return {'EUR': 2}


def test_two_backends():
    """
    Two different backends should not interfere with each other.
    """
    one = FixedOneBackend()
    two = FixedTwoBackend()
    one.update_rates()
    two.update_rates()
    for backend in (one, two):
        assert Rate.objects.filter(backend__name=backend.name).count() == 1
