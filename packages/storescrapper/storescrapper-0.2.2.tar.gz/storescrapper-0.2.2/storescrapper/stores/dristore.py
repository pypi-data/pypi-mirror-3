from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class Dristore(Store):
    @classmethod
    def product_types(cls):
        return [
            'VideoCard',
            'Processor',
            'Monitor',
            'Ram',
            'StorageDrive',
            'PowerSupply',
            'ComputerCase',
        ]

    @classmethod
    def _retrieve_product(cls, url):
        soup = BeautifulSoup(mechanize.urlopen(url))

        name = soup.find('h1').string.strip().encode('ascii', 'ignore')

        if soup.find('span', 'warning_inline'):
            return [name, None]

        prices = {}

        cash_price = soup.find('span', {'id': 'our_price_display'}).string
        cash_price = Decimal(clean_price_string(cash_price))

        for p in ['cash', 'deposit', 'wire_transfer']:
            prices[p] = cash_price

        normal_price = soup.find('span', 'value').string
        normal_price = Decimal(clean_price_string(normal_price))

        for p in ['debit_card', 'credit_card']:
            prices[p] = normal_price

        return [name, prices]

    @classmethod
    def _product_urls_and_types(cls, product_types):
        product_urls_and_types = {}

        url_extensions = [
            ['33-discos-duros', 'StorageDrive'],
            ['28-fuentes-de-poder', 'PowerSupply'],
            ['47-gabinetes', 'ComputerCase'],
            ['29-memorias-ram', 'Ram'],
            ['55-monitores', 'Monitor'],
            ['54-procesadores', 'Processor'],
            ['52-tarjetas-de-video', 'VideoCard'],
        ]

        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue
            p = 1

            while True:
                url = 'http://www.dristore.cl/catalogo/' + url_extension + \
                      '?p=' + str(p)
                base_soup = BeautifulSoup(mechanize.urlopen(url))

                product_urls = [li.find('a')['href'] for li in
                                base_soup.findAll('li', 'ajax_block_product')]

                flag = False

                for url in product_urls:
                    if url in product_urls_and_types:
                        flag = True
                        break
                    product_urls_and_types[url] = ptype

                if flag:
                    break

                p += 1

        return product_urls_and_types.items()
