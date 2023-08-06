from decimal import Decimal
import unittest
from storescrapper.product import Product


class TestProduct(unittest.TestCase):
    def setUp(self):
        self.product = Product(u'Product1', {'cash': Decimal(149990)},
            u'http://www.example.com/product_1', u'Notebook', u'FooStore')
        self.not_available_product = Product(u'Product2', {},
            u'http://www.example.com/product_2', u'Notebook', u'FooStore')

    def test_is_available(self):
        self.assertTrue(self.product.is_available())
        self.assertFalse(self.not_available_product.is_available())

    def test_product_creation(self):
        self.assertEqual('Product1', self.product.name)
        self.assertEqual({'cash': Decimal(149990)},
            self.product.payment_method_prices)
        self.assertEqual('http://www.example.com/product_1', self.product.url)
        self.assertEqual('Notebook', self.product.type)
        self.assertEqual('FooStore', self.product.store)

    def test_product_unicode(self):
        self.assertEqual('FooStore - Product1 (Notebook)\n'
                         'http://www.example.com/product_1\ncash: $149.990\n',
            unicode(self.product))

    def test_product_str(self):
        self.assertEqual('FooStore - Product1 (Notebook)\n'
                         'http://www.example.com/product_1\ncash: $149.990\n',
            str(self.product))

    def test_product_repr(self):
        self.assertEqual('FooStore - Product1 (Notebook)\n'
                         'http://www.example.com/product_1\ncash: $149.990\n',
            repr(self.product))

    def test_not_available_product_unicode(self):
        self.assertEqual(u'FooStore - Product2 (Notebook)\n'
                         u'http://www.example.com/product_2\nNot available\n',
            unicode(self.not_available_product))

    def test_product_equality(self):
        another_product = Product(u'Product1', {'cash': Decimal(149990)},
            u'http://www.example.com/product_1', u'Notebook', u'FooStore')
        self.assertEqual(another_product, self.product)

    def test_product_inequality(self):
        changed_attrs = [
            ['name', 'product1'],
            ['payment_method_prices', {'cash': Decimal(150000)}],
            ['url', 'http://example.com/product_1'],
            ['type', 'Notebooks'],
            ['store', 'BarStore'],
        ]

        for attr, new_value in changed_attrs:
            another_product = Product(u'Product1', {'cash': Decimal(149990)},
                u'http://www.example.com/product_1', u'Notebook', u'FooStore')
            setattr(another_product, attr, new_value)
            self.assertNotEquals(another_product, self.product)
