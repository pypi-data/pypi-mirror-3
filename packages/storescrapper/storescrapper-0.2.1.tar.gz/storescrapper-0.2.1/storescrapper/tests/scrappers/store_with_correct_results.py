from decimal import Decimal
from storescrapper.store import Store


class StoreWithCorrectResults(Store):
    @classmethod
    def _retrieve_product(cls, url):
        d = dict(joined_key_value.split('=') for joined_key_value in
        url.split('?')[1].split('&'))

        name = d['product']
        price = {'cash': Decimal(d['price'])}

        if 'not-available' in url:
            price = {}

        return [name, price]

    @classmethod
    def _product_urls_and_types(cls, product_types):
        data = [
            ('http://dummystore.com/?product=dm1-3060&price=199990',
             'Notebook'),
            ('http://dummystore.com/?product=sapphire-hd6850&'
             'availability=not-available&price=105500', 'VideoCard'),
            ('http://dummystore.com/?product='
             'intel-core-i5-2500k&price=145500', 'Processor'),
        ]

        result = []

        for url, type in data:
            if product_types and type in product_types:
                result.append([url, type])

        return result

    @classmethod
    def product_types(cls):
        return ['Notebook', 'VideoCard', 'Processor']
