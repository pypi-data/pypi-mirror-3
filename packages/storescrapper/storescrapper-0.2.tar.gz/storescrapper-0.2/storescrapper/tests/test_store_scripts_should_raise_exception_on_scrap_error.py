import unittest
from storescrapper.exceptions.store_scrap_error import StoreScrapError
from storescrapper.tests.scrappers.store_with_scrap_error import \
    StoreWithScrapError


class TestStoreScriptsShouldRaiseErrorOnScrapError(unittest.TestCase):

    def setUp(self):
        self.store = StoreWithScrapError

    def test_retrieve_product(self):
        product_url = u'http://www.example.com/invalid_product'
        with self.assertRaises(StoreScrapError):
            self.store.retrieve_product(product_url, u'Notebook')

    def test_product_urls_and_types_with_async(self):
        with self.assertRaises(StoreScrapError):
            self.store.product_urls_and_types(product_types=[u'Notebook'])

    def test_product_urls_and_types_without_async(self):
        with self.assertRaises(StoreScrapError):
            self.store.product_urls_and_types(product_types=[u'StorageDrive'],
                async=False)

    def test_products_with_async(self):
        with self.assertRaises(StoreScrapError):
            self.store.products(product_types=[u'VideoCard'])

    def test_products_without_async(self):
        with self.assertRaises(StoreScrapError):
            self.store.products(product_types=[u'VideoCard'], async=False)

    def test_products_with_safe_urls(self):
        with self.assertRaises(StoreScrapError):
            self.store.products(product_types=[u'SkipError'])
