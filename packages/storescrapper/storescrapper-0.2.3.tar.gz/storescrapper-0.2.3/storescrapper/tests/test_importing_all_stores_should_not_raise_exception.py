import unittest


class TestImportingAllStoresShouldNotRaiseException(unittest.TestCase):

    def test_import_all_stores(self):
        __import__('storescrapper.stores', globals(), locals(), ['*'])
