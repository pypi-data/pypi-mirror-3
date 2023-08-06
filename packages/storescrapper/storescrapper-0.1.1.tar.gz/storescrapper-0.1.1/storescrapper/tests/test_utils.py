from decimal import Decimal
import unittest
from storescrapper.utils import count_decimals, format_currency
from storescrapper.utils import clean_price_string


class TestUtils(unittest.TestCase):

    def test_clean_price_string(self):
        value_expected_pairs = [['199.990', '199990'], ['990,990', '990990'],
            ['$19.990', '19990'], ['$105.500', '105500']]
        for dec_string, expected_value in value_expected_pairs:
            self.assertEqual(expected_value, clean_price_string(dec_string))

    def test_count_decimals(self):
        value_expected_pairs = [['123.45', 2], ['42', 0], ['-105.785', 3],
            ['-99', 0], ['87.', 0]]
        for decimal_string, expected_value in value_expected_pairs:
            value = Decimal(decimal_string)
            self.assertEqual(expected_value, count_decimals(value))

    def test_format_currency(self):
        value_expected_pairs = [['199990', '$199.990'], ['990', '$990'],
            ['29.95', '$29,95'], ['1010990', '$1.010.990'],
            ['-0.99', '-$0,99']]
        for decimal_string, expected_value in value_expected_pairs:
            value = Decimal(decimal_string)
            self.assertEqual(expected_value, format_currency(value))

    def test_init_tests(self):
        __import__('storescrapper.tests')
