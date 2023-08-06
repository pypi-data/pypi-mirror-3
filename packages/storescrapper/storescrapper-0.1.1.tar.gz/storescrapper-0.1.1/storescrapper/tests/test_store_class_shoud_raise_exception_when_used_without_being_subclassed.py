import unittest
from storescrapper.store import Store


class TestStoreClassShouldRaiseExceptionWhenUsedWithoutBeingSubclassed(
    unittest.TestCase):

    def setUp(self):
        self.store = Store()

    def test_product_urls_and_types_with_async(self):
        with self.assertRaises(NotImplementedError):
            self.store.product_urls_and_types(product_types=('Notebook', ))

    def test_product_urls_and_types_without_async(self):
        with self.assertRaises(NotImplementedError):
            self.store.product_urls_and_types(product_types=('Processor', ),
                async=False)

    def test_retrieve_product(self):
        with self.assertRaises(NotImplementedError):
            self.store.retrieve_product(
                url='http://www.example.com/dummy_product',
                product_type='PowerSupply')

    def test_products_with_async(self):
        with self.assertRaises(NotImplementedError):
            self.store.products(product_types=('Notebook', ))

    def test_products_without_async(self):
        with self.assertRaises(NotImplementedError):
            self.store.products(product_types=('Notebook', ), async=False)
