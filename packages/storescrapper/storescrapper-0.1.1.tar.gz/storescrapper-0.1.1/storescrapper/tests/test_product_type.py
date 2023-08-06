import unittest
from storescrapper.product_type import ProductType


class TestProductType(unittest.TestCase):

    def test_valid_product_type(self):
        self.assertTrue(ProductType.is_valid_type('Processor'))

    def test_invalid_product_type(self):
        self.assertFalse(ProductType.is_valid_type('Bycicle'))
