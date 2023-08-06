from decimal import Decimal
from httplib import BadStatusLine
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class Onak(Store):
    @classmethod
    def product_types(cls):
        return [
            'Notebook',
            'VideoCard',
            'Processor',
            'Monitor',
            'Television',
            'Motherboard',
            'Ram',
            'StorageDrive',
            'PowerSupply',
            'ComputerCase'
        ]

    @classmethod
    def _retrieve_product(cls, url):
        br = mechanize.Browser()
        try:
            data = br.open(url).get_data()
        except BadStatusLine:
            return url, {}
        soup = BeautifulSoup(data)

        name = soup.findAll('h1')[1].string.strip().encode('ascii', 'ignore')

        contado_price = Decimal(
            clean_price_string(soup.findAll('span', 'price')[1].string))

        normal_price = Decimal(
            clean_price_string(soup.findAll('span', 'price')[3].string))

        prices = {}
        for payment_method in ['wire_transfer', 'deposit', 'cash']:
            prices[payment_method] = contado_price

        for payment_method in ['debit_card', 'credit_card', 'presto_card']:
            prices[payment_method] = normal_price

        return name, prices

    @classmethod
    def _product_urls_and_types(cls, product_types):
        # Basic data of the target webpage and the specific catalog
        url_base = 'http://www.onak.cl/'

        # Browser initialization
        browser = mechanize.Browser()

        url_extensions = [
            ['pc-servidores/notebooks.html', 'Notebook'],
            ['pc-servidores/netbooks.html', 'Notebook'],
            ['almacenamiento/discos-duro.html', 'StorageDrive'],
            ['multimedia/televisores.html', 'Television'],
            ['componentes/memorias-ram-1.html', 'Ram'],
            ['componentes/fuentes-poder.html', 'PowerSupply'],
            ['componentes/procesadores.html', 'Processor'],
            ['componentes/placas-madre.html', 'Motherboard'],
            ['componentes/tarjetas-video.html', 'VideoCard'],
            ['componentes/monitores.html', 'Monitor'],
            ['componentes/gabinetes.html', 'ComputerCase'],
        ]

        product_urls = {}

        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue

            page_number = 1

            while True:
                url = url_base + url_extension + '?limit=32&p=' + \
                    str(page_number)
                soup = BeautifulSoup(browser.open(url).get_data())

                product_table = soup.find(
                    'table', {'id': 'product-list-table'})

                if not product_table:
                    break

                product_paragraphs = product_table.findAll(
                    'p', 'product-image')

                done = False

                for p in product_paragraphs:
                    product_url = p.find('a')['href']
                    if product_url in product_urls:
                        done = True
                        break
                    product_urls[product_url] = ptype

                if done:
                    break

                page_number += 1

        return product_urls.items()
