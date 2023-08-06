from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class PcFactory(Store):
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
            'PowerSupply'
        ]

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()
        soup = BeautifulSoup(browser.open(url).get_data())

        name_container = soup.find('span', 'main_titulo_ficha_bold')
        name_pieces = name_container.string.encode('ascii', 'ignore').split()
        name = ' '.join(name_pieces)

        prices = {}

        cash_price = soup.find('span', 'main_precio_efectivo').find(
            'strong').string
        cash_price = Decimal(clean_price_string(cash_price.string))

        for p in ['cash', 'deposit', 'wire_transfer']:
            prices[p] = cash_price

        normal_price = soup.find('span', 'main_precio_normal').find(
            'strong').string[:-1]
        normal_price = int(clean_price_string(normal_price))

        for p in ['check', 'debit_card']:
            prices[p] = Decimal(int(round(normal_price * 0.97)))

        for p in ['credit_card', 'ripley_card', 'presto_card']:
            prices[p] = Decimal(normal_price)

        return name, prices

    @classmethod
    def _product_urls_and_types(cls, product_types):
        url_base = 'http://www.pcfactory.cl'

        browser = mechanize.Browser()

        url_extensions = [
            ['?categoria=425', 'Notebook'],
            ['?categoria=334', 'VideoCard'],
            ['?categoria=272', 'Processor'],
            ['?papa=256&categoria=250', 'Monitor'],  # Monitores LCD
            ['?papa=256&categoria=260', 'Television'],  # Televisores LCD
            ['?categoria=292', 'Motherboard'],
            ['?papa=264&categoria=112', 'Ram'],  # Memoria PC
            ['?papa=264&categoria=482', 'Ram'],  # Memoria PC High-End
            ['?papa=264&categoria=100', 'Ram'],  # Memoria Notebook
            ['?papa=264&categoria=266', 'Ram'],  # Memoria Server
            ['?papa=312&categoria=340', 'StorageDrive'],  # HDD PC
            ['?papa=312&categoria=421', 'StorageDrive'],  # HDD Notebook
            ['?papa=326&categoria=54', 'PowerSupply'],  # Fuentes de poder
        ]

        product_links = {}
        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue

            url = url_base + '/' + url_extension

            soup = BeautifulSoup(browser.open(url).get_data())

            try:
                page_count = soup.findAll('table',
                        {'class': 'descripcionbold'})
                page_count = page_count[1].findAll('td', {'align': 'center'})
                page_count = int(page_count[-1].find('a').string)
            except Exception:
                page_count = 1

            for page in range(page_count):
                page += 1

                complete_url = url + '&pagina=' + str(page)

                soup = BeautifulSoup(browser.open(complete_url).get_data())

                product_link_tags = soup.findAll('a',
                        {'class': 'vinculoNombreProd'})

                for product_link in product_link_tags:
                    link = url_base + product_link['href']
                    link = link.encode('ascii', 'ignore')
                    if link not in product_links:
                        product_links[link] = ptype

        return product_links.items()
