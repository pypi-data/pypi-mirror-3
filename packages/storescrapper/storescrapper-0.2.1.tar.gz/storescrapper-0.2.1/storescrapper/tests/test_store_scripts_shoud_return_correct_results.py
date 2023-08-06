from decimal import Decimal
import unittest
from storescrapper.product import Product
from storescrapper.tests.scrappers.store_with_correct_results import \
    StoreWithCorrectResults


class TestStoreScriptsShouldReturnCorrectResults(unittest.TestCase):

    def setUp(self):
        self.store = StoreWithCorrectResults

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

    def test_product_urls_and_types_without_args_with_async(self):
        product_urls_and_types = self.store.product_urls_and_types()
        self.assertEquals([
            ('http://dummystore.com/?product=dm1-3060&price=199990',
             'Notebook',),
            ('http://dummystore.com/?product=sapphire-hd6850&'
             'availability=not-available&price=105500', 'VideoCard',),
            ('http://dummystore.com/?product='
             'intel-core-i5-2500k&price=145500', 'Processor',),
        ], product_urls_and_types)

    def test_product_urls_and_types_without_args_without_async(self):
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
            url=u'http://dummystore.com/?product=sapphire-hd6850&' \
                u'availability=not-available&price=105500',
            product_type=u'VideoCard')
        expected_product = Product(u'sapphire-hd6850', {},
            u'http://dummystore.com/?product=sapphire-hd6850&'
            u'availability=not-available&price=105500', u'VideoCard',
            u'StoreWithCorrectResults')

        self.assertEquals(expected_product, product)

        product = self.store.retrieve_product(
            url=u'http://dummystore.com/?product=intel-core-i5-2500k&' \
                u'price=145500',
            product_type=u'Processor')
        expected_product = Product(u'intel-core-i5-2500k',
                {'cash': Decimal(145500)},
            u'http://dummystore.com/?product=intel-core-i5-2500k&price=145500',
            u'Processor', u'StoreWithCorrectResults')
        self.assertEquals(expected_product, product)

    def test_all_products_with_async(self):
        products = self.store.products([u'Notebook', u'VideoCard',
                                        u'Processor'])

        expected_products = [
            Product(u'dm1-3060', {'cash': Decimal(199990)},
                u'http://dummystore.com/?product=dm1-3060&price=199990',
                u'Notebook', u'StoreWithCorrectResults'),
            Product(u'sapphire-hd6850', {},
                u'http://dummystore.com/?product=sapphire-hd6850&'
                u'availability=not-available&price=105500', u'VideoCard',
                u'StoreWithCorrectResults'),
            Product(u'intel-core-i5-2500k', {'cash': Decimal(145500)},
                u'http://dummystore.com/?product=intel-core-i5-2500k&'
                u'price=145500', u'Processor', u'StoreWithCorrectResults'),
        ]

        self.assertEquals(expected_products, products)

    def test_products_without_args_with_async(self):
        products = self.store.products()

        expected_products = [
            Product(u'dm1-3060', {'cash': Decimal(199990)},
                u'http://dummystore.com/?product=dm1-3060&price=199990',
                u'Notebook', u'StoreWithCorrectResults'),
            Product(u'sapphire-hd6850', {},
                u'http://dummystore.com/?product=sapphire-hd6850&'
                u'availability=not-available&price=105500', u'VideoCard',
                u'StoreWithCorrectResults'),
            Product(u'intel-core-i5-2500k', {'cash': Decimal(145500)},
                u'http://dummystore.com/?product=intel-core-i5-2500k&'
                u'price=145500', u'Processor', u'StoreWithCorrectResults'),
            ]

        self.assertEquals(expected_products, products)

    def test_subset_products_with_async(self):
        products = self.store.products(product_types=[u'Notebook'])
        expected_products = [
            Product(u'dm1-3060', {'cash': Decimal(199990)},
                u'http://dummystore.com/?product=dm1-3060&price=199990',
                u'Notebook', u'StoreWithCorrectResults')
        ]

        self.assertEquals(expected_products, products)

    def test_all_products_without_async(self):
        products = self.store.products([u'Notebook', u'VideoCard',
                                        u'Processor'],
            async=False)
        expected_products = [
            Product(u'dm1-3060', {'cash': Decimal(199990)},
                u'http://dummystore.com/?product=dm1-3060&price=199990',
                u'Notebook', u'StoreWithCorrectResults'),
            Product(u'sapphire-hd6850', {},
                u'http://dummystore.com/?product=sapphire-hd6850&'
                u'availability=not-available&price=105500', u'VideoCard',
                u'StoreWithCorrectResults'),
            Product(u'intel-core-i5-2500k', {'cash': Decimal(145500)},
                u'http://dummystore.com/?product=intel-core-i5-2500k&'
                u'price=145500', u'Processor', u'StoreWithCorrectResults')
        ]

        self.assertEquals(expected_products, products)

    def test_subset_products_without_async(self):
        products = self.store.products(product_types=[u'Notebook', ],
            async=False)
        expected_products = [
            Product(u'dm1-3060', {'cash': Decimal(199990)},
                u'http://dummystore.com/?product=dm1-3060&price=199990',
                u'Notebook', u'StoreWithCorrectResults')
        ]

        self.assertEquals(expected_products, products)

    def test_products_without_args_without_async(self):
        products = self.store.products(async=False)

        expected_products = [
            Product(u'dm1-3060', {'cash': Decimal(199990)},
                u'http://dummystore.com/?product=dm1-3060&price=199990',
                u'Notebook', u'StoreWithCorrectResults'),
            Product(u'sapphire-hd6850', {},
                u'http://dummystore.com/?product=sapphire-hd6850&'
                u'availability=not-available&price=105500', u'VideoCard',
                u'StoreWithCorrectResults'),
            Product(u'intel-core-i5-2500k', {'cash': Decimal(145500)},
                u'http://dummystore.com/?product=intel-core-i5-2500k&'
                u'price=145500', u'Processor', u'StoreWithCorrectResults'),
            ]

        self.assertEquals(expected_products, products)
