from decimal import Decimal
import unittest
from storescrapper.product import Product


class TestProduct(unittest.TestCase):
    def setUp(self):
        self.product = Product('Product1', Decimal(149990),
            'http://www.example.com/product_1', 'Notebook', 'FooStore')

    def test_product_creation(self):
        self.assertEqual('Product1', self.product.name)
        self.assertEqual(Decimal(149990), self.product.price)
        self.assertEqual('http://www.example.com/product_1', self.product.url)
        self.assertEqual('Notebook', self.product.type)
        self.assertEqual('FooStore', self.product.store)

    def test_product_unicode(self):
        self.assertEqual('FooStore - Product1 (Notebook)\n'
                         'http://www.example.com/product_1\n$149.990',
            unicode(self.product))

    def test_product_str(self):
        self.assertEqual('FooStore - Product1 (Notebook)\n'
                         'http://www.example.com/product_1\n$149.990',
            str(self.product))

    def test_product_repr(self):
        self.assertEqual('FooStore - Product1 (Notebook)\n'
                         'http://www.example.com/product_1\n$149.990',
            repr(self.product))

    def test_product_equality(self):
        another_product = Product('Product1', Decimal(149990),
            'http://www.example.com/product_1', 'Notebook', 'FooStore')
        self.assertEqual(another_product, self.product)

    def test_product_inequality(self):
        changed_attrs = [
            ['name', 'product1'],
            ['price', Decimal(150000)],
            ['url', 'http://example.com/product_1'],
            ['type', 'Notebooks'],
            ['store', 'BarStore'],
        ]

        for attr, new_value in changed_attrs:
            another_product = Product('Product1', Decimal(149990),
                'http://www.example.com/product_1', 'Notebook', 'FooStore')
            setattr(another_product, attr, new_value)
            self.assertNotEquals(another_product, self.product)
