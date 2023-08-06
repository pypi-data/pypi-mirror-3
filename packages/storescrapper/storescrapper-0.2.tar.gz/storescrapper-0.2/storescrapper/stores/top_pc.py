from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class TopPc(Store):
    @classmethod
    def product_types(cls):
        return [
            'Notebook',
            'VideoCard',
            'Processor',
            'Monitor',
            'Television'
            'Motherboard',
            'Ram',
            'StorageDrive',
            'PowerSupply',
            ]

    @classmethod
    def _retrieve_product(cls, url):
        br = mechanize.Browser()
        soup = BeautifulSoup(br.open(url).get_data())

        name = soup.find('h2').string

        prices = {}

        cash_price = soup.find('span', {'id': 'our_price_display'}).string
        cash_price = Decimal(clean_price_string(cash_price))

        prices['cash'] = cash_price

        normal_price = soup.find('span', {'id': 'old_price_display'}).string
        normal_price = Decimal(clean_price_string(normal_price))

        for p in ['debit_card', 'credit_card']:
            prices[p] = normal_price

        return name, prices

    @classmethod
    def _product_urls_and_types(cls, product_types):
        browser = mechanize.Browser()

        url_extensions = [
            ['76', 'VideoCard'],    # Tarjetas de video
            ['5', 'Processor'],     # Procesadores
            ['110', 'Monitor'],    # Monitores
            ['111', 'Television'],    # Televisions
            ['153', 'Notebook'],   # Notebooks
            ['63', 'Notebook'],   # Netbook
            ['234', 'Notebook'],   # Apple notebooks
            ['8', 'Motherboard'],   # MB
            ['11', 'Ram'],   # RAM
            ['16', 'StorageDrive'],   # HDD IDE
            ['17', 'StorageDrive'],   # HDD SATA
            ['20', 'PowerSupply'],   # Fuentes de poder
        ]

        product_links = []

        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue
            url = 'http://www.toppc.cl/beta/category.php?n=50&id_category=' + \
                  url_extension

            soup = BeautifulSoup(browser.open(url).get_data())
            raw_links = soup.findAll('a', {'class': 'product_img_link'})

            for raw_link in raw_links:
                link = raw_link['href']
                product_links.append([link, ptype])

        return product_links
