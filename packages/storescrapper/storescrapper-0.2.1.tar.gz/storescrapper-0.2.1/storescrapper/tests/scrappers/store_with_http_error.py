from decimal import Decimal
import mechanize
from storescrapper.store import Store


class StoreWithHttpError(Store):
    already_raised_http_error = False

    @classmethod
    def _retrieve_product(cls, url):
        if not cls.already_raised_http_error:
            cls.already_raised_http_error = True
            raise mechanize.HTTPError(None, None, None, None, None)

        d = dict(joined_key_value.split('=') for joined_key_value in
        url.split('?')[1].split('&'))

        name = d['product']
        price = {'cash': Decimal(d['price'])}

        return [name, price]
