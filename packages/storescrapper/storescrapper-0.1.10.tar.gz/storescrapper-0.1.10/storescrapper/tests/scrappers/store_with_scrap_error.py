from storescrapper.store import Store


class StoreWithScrapError(Store):
    @classmethod
    def product_types(cls):
        return ['Notebook', 'VideoCard', 'StorageDrive', 'SkipError']

    @classmethod
    def _retrieve_product(cls, url):
        raise Exception('Forced exception')

    @classmethod
    def _product_urls_and_types(cls, product_types):
        if 'SkipError' in product_types:
            return [('dummyurl', 'dummytype')]
        raise Exception('Forced exception')
