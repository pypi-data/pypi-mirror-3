from decimal import Decimal
import unittest
from storescrapper.product import Product
from storescrapper.store import Store


class TestStoreScriptsShouldReturnCorrectResults(unittest.TestCase):

    def setUp(self):
        class DummyStore(Store):
            @classmethod
            def _retrieve_product(cls, url):
                if 'not-available' in url:
                    return None

                d = dict(joined_key_value.split('=') for joined_key_value in
                    url.split('?')[1].split('&'))

                name = d['product']
                price = Decimal(d['price'])

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

                for ptype in product_types:
                    for url, type in data:
                        if ptype == type:
                            result.append([url, ptype])

                return result
        self.store = DummyStore

    def test_product_urls_and_types_with_async(self):
        product_urls_and_types = self.store.product_urls_and_types()
        self.assertEquals([
            ('http://dummystore.com/?product=dm1-3060&price=199990',
             'Notebook',),
            ('http://dummystore.com/?product=sapphire-hd6850&'
             'availability=not-available&price=105500', 'VideoCard',),
            ('http://dummystore.com/?product='
             'intel-core-i5-2500k&price=145500', 'Processor',),
        ], product_urls_and_types)

    def test_product_urls_and_types_without_async(self):
        product_urls_and_types = self.store.product_urls_and_types(async=False)
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
            url='http://dummystore.com/?product=sapphire-hd6850&' \
                'availability=not-available&price=105500',
            product_type='VideoCard')
        self.assertIsNone(product)

        product = self.store.retrieve_product(
            url='http://dummystore.com/?product=intel-core-i5-2500k&' \
                'price=145500',
            product_type='Processor')
        expected_product = Product('intel-core-i5-2500k', Decimal(145500),
            'http://dummystore.com/?product=intel-core-i5-2500k&price=145500',
            'Processor', 'DummyStore')
        self.assertEquals(expected_product, product)

    def test_all_products_with_async(self):
        products = self.store.products()
        expected_products = [
            Product('dm1-3060', Decimal(199990),
                'http://dummystore.com/?product=dm1-3060&price=199990',
                'Notebook', 'DummyStore'),
            Product('intel-core-i5-2500k', Decimal(145500),
                'http://dummystore.com/?product=intel-core-i5-2500k&'
                'price=145500', 'Processor', 'DummyStore')
        ]

        self.assertEquals(expected_products, products)

    def test_subset_products_with_async(self):
        products = self.store.products(product_types=('Notebook', ))
        expected_products = [
            Product('dm1-3060', Decimal(199990),
                'http://dummystore.com/?product=dm1-3060&price=199990',
                'Notebook', 'DummyStore')
        ]

        self.assertEquals(expected_products, products)

    def test_all_products_without_async(self):
        products = self.store.products(async=False)
        expected_products = [
            Product('dm1-3060', Decimal(199990),
                'http://dummystore.com/?product=dm1-3060&price=199990',
                'Notebook', 'DummyStore'),
            Product('intel-core-i5-2500k', Decimal(145500),
                'http://dummystore.com/?product=intel-core-i5-2500k&'
                'price=145500', 'Processor', 'DummyStore')
        ]

        self.assertEquals(expected_products, products)

    def test_subset_products_without_async(self):
        products = self.store.products(product_types=('Notebook', ),
            async=False)
        expected_products = [
            Product('dm1-3060', Decimal(199990),
                'http://dummystore.com/?product=dm1-3060&price=199990',
                'Notebook', 'DummyStore')
        ]

        self.assertEquals(expected_products, products)
