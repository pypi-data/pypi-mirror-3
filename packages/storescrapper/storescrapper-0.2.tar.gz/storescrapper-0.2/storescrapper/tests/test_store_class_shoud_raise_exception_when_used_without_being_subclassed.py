import unittest
from storescrapper.store import Store


class TestStoreClassShouldRaiseExceptionWhenUsedWithoutBeingSubclassed(
    unittest.TestCase):

    def setUp(self):
        self.store = Store()

    def test_product_urls_and_types_with_async(self):
        with self.assertRaises(NotImplementedError):
            self.store.product_urls_and_types(product_types=[u'Notebook', ])

    def test_product_urls_and_types_without_async(self):
        with self.assertRaises(NotImplementedError):
            self.store.product_urls_and_types(product_types=[u'Notebook', ],
            async=False)

    def test_product_urls_and_types_wrapper(self):
        with self.assertRaises(NotImplementedError):
            self.store._product_urls_and_types_wrapper(
                product_types=[u'Processor', ],)

    def test_product_types_without_async(self):
        with self.assertRaises(NotImplementedError):
            self.store.product_types()

    def test_retrieve_product(self):
        with self.assertRaises(NotImplementedError):
            self.store.retrieve_product(
                url=u'http://www.example.com/dummy_product',
                product_type=u'PowerSupply')

    def test_products_with_async(self):
        with self.assertRaises(NotImplementedError):
            self.store.products(product_types=[u'Notebook', ])

    def test_products_without_async(self):
        with self.assertRaises(NotImplementedError):
            self.store.products(product_types=[u'Notebook', ], async=False)
