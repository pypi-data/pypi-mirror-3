import unittest


class TestImportingAllStoresShouldNotRaiseException(unittest.TestCase):

    def test_import_all_stores(self):
        try:
            __import__('storescrapper.stores', globals(), locals(), ['*'])
        except Exception, e:
            self.fail(e.message)
