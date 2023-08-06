from decimal import Decimal
import unittest
from storescrapper.product import Product
from storescrapper.store import Store


class TestStoreScriptsShouldReturnCorrectResults(unittest.TestCase):

    def setUp(self):
        class DummyStore(Store):
            @classmethod
            def _retrieve_product(cls, url):
                d = dict(joined_key_value.split('=') for joined_key_value in
                    url.split('?')[1].split('&'))

                name = d['product']
                price = Decimal(d['price'])

                if 'not-available' in url:
                    price = None

                return [name, price]

            @classmethod
            def _product_urls_and_types(cls, product_types):
                data = [
                    ('http://dummystore.com/?product=dm1-3060&price=199990',
                     'Notebook'),
                    ('http://dummystore.com/?product=sapphire-hd6850&'
                     'availability=not-available&price=105500', 'VideoCard'),
                    ('http://dummystore.com/?product='
                     'intel-core-i5-2500k&price=145500', 'Processor'),
                ]

                result = []

                for url, type in data:
                    if product_types and type in product_types:
                        result.append([url, type])

                return result
        self.store = DummyStore

    def test_product_urls_and_types_with_async(self):
        product_urls_and_types = self.store.product_urls_and_types(
            [u'Notebook', u'VideoCard', u'Processor'])
        self.assertEquals([
            ('http://dummystore.com/?product=dm1-3060&price=199990',
             'Notebook',),
            ('http://dummystore.com/?product=sapphire-hd6850&'
             'availability=not-available&price=105500', 'VideoCard',),
            ('http://dummystore.com/?product='
             'intel-core-i5-2500k&price=145500', 'Processor',),
        ], product_urls_and_types)

    def test_product_urls_and_types_without_async(self):
        product_urls_and_types = self.store.product_urls_and_types(
            [u'Notebook', u'VideoCard', u'Processor'], async=False)
        self.assertEquals([
            ('http://dummystore.com/?product=dm1-3060&price=199990',
             'Notebook',),
            ('http://dummystore.com/?product=sapphire-hd6850&'
             'availability=not-available&price=105500', 'VideoCard',),
            ('http://dummystore.com/?product='
             'intel-core-i5-2500k&price=145500', 'Processor',),
        ], product_urls_and_types)

    def test_retrieve_product(self):
        product = self.store.retrieve_product(
            url=u'http://dummystore.com/?product=sapphire-hd6850&' \
                u'availability=not-available&price=105500',
            product_type=u'VideoCard')
        expected_product = Product(u'sapphire-hd6850', None,
            u'http://dummystore.com/?product=sapphire-hd6850&'
            u'availability=not-available&price=105500', u'VideoCard',
            u'DummyStore')

        self.assertEquals(expected_product, product)

        product = self.store.retrieve_product(
            url=u'http://dummystore.com/?product=intel-core-i5-2500k&' \
                u'price=145500',
            product_type=u'Processor')
        expected_product = Product(u'intel-core-i5-2500k', Decimal(145500),
            u'http://dummystore.com/?product=intel-core-i5-2500k&price=145500',
            u'Processor', u'DummyStore')
        self.assertEquals(expected_product, product)

    def test_all_products_with_async(self):
        products = self.store.products([u'Notebook', u'VideoCard',
                                        u'Processor'])

        expected_products = [
            Product(u'dm1-3060', Decimal(199990),
                u'http://dummystore.com/?product=dm1-3060&price=199990',
                u'Notebook', u'DummyStore'),
            Product(u'sapphire-hd6850', None,
                u'http://dummystore.com/?product=sapphire-hd6850&'
                u'availability=not-available&price=105500', u'VideoCard',
                u'DummyStore'),
            Product(u'intel-core-i5-2500k', Decimal(145500),
                u'http://dummystore.com/?product=intel-core-i5-2500k&'
                u'price=145500', u'Processor', u'DummyStore'),
        ]

        self.assertEquals(expected_products, products)

    def test_subset_products_with_async(self):
        products = self.store.products(product_types=[u'Notebook'])
        expected_products = [
            Product(u'dm1-3060', Decimal(199990),
                u'http://dummystore.com/?product=dm1-3060&price=199990',
                u'Notebook', u'DummyStore')
        ]

        self.assertEquals(expected_products, products)

    def test_all_products_without_async(self):
        products = self.store.products([u'Notebook', u'VideoCard',
                                        u'Processor'],
            async=False)
        expected_products = [
            Product(u'dm1-3060', Decimal(199990),
                u'http://dummystore.com/?product=dm1-3060&price=199990',
                u'Notebook', u'DummyStore'),
            Product(u'sapphire-hd6850', None,
                u'http://dummystore.com/?product=sapphire-hd6850&'
                u'availability=not-available&price=105500', u'VideoCard',
                u'DummyStore'),
            Product(u'intel-core-i5-2500k', Decimal(145500),
                u'http://dummystore.com/?product=intel-core-i5-2500k&'
                u'price=145500', u'Processor', u'DummyStore')
        ]

        self.assertEquals(expected_products, products)

    def test_subset_products_without_async(self):
        products = self.store.products(product_types=[u'Notebook', ],
            async=False)
        expected_products = [
            Product(u'dm1-3060', Decimal(199990),
                u'http://dummystore.com/?product=dm1-3060&price=199990',
                u'Notebook', u'DummyStore')
        ]

        self.assertEquals(expected_products, products)
