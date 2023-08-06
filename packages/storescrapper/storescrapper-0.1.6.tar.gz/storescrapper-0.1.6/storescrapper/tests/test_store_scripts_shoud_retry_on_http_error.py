from decimal import Decimal
import unittest
import mechanize
from storescrapper.product import Product
from storescrapper.store import Store


class TestStoreScriptsShouldRetryOnHttpError(unittest.TestCase):

    def setUp(self):
        class DummyStoreWithHttpError(Store):
            already_raised_http_error = False

            @classmethod
            def _retrieve_product(cls, url):
                if not cls.already_raised_http_error:
                    cls.already_raised_http_error = True
                    raise mechanize.HTTPError(None, None, None, None, None)

                d = dict(joined_key_value.split('=') for joined_key_value in
                    url.split('?')[1].split('&'))

                name = d['product']
                price = Decimal(d['price'])

                return [name, price]

        self.store = DummyStoreWithHttpError

    def test_retrieve_product_on_http_error(self):
        product = self.store.retrieve_product(
            url=u'http://dummystore.com/?product=intel-core-i5-2500k&'\
                u'price=145500',
            product_type=u'Processor')
        expected_product = Product(u'intel-core-i5-2500k', Decimal(145500),
            u'http://dummystore.com/?product=intel-core-i5-2500k&price=145500',
            u'Processor', u'DummyStoreWithHttpError')
        self.assertEquals(expected_product, product)
