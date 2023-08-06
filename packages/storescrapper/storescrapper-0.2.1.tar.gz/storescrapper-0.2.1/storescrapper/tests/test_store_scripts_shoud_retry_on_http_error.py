from decimal import Decimal
import unittest
from storescrapper.product import Product
from storescrapper.tests.scrappers.store_with_http_error import \
    StoreWithHttpError


class TestStoreScriptsShouldRetryOnHttpError(unittest.TestCase):

    def setUp(self):
        self.store = StoreWithHttpError

    def test_retrieve_product_on_http_error(self):
        product = self.store.retrieve_product(
            url=u'http://dummystore.com/?product=intel-core-i5-2500k&'\
                u'price=145500',
            product_type=u'Processor')
        expected_product = Product(u'intel-core-i5-2500k',
                {'cash': Decimal(145500)},
            u'http://dummystore.com/?product=intel-core-i5-2500k&price=145500',
            u'Processor', u'StoreWithHttpError')
        self.assertEquals(expected_product, product)
