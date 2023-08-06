from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class PcExpress(Store):
    force_sync = True

    @classmethod
    def product_types(cls):
        return [
            'Notebook',
            'VideoCard',
            'Processor',
            'Monitor',
            'Motherboard',
            'Ram',
            'StorageDrive',
            'PowerSupply'
        ]

    @classmethod
    def _retrieve_product(cls, url):
        br = mechanize.Browser()
        data = br.open(url).get_data()
        soup = BeautifulSoup(data)

        name = soup.find('h1').string.encode('ascii', 'ignore')

        prices = {}

        contado_price = soup.find('span', {'class': 'precio oferta'}).find('b')
        contado_price = Decimal(clean_price_string(contado_price.string))

        for p in ['cash', 'check', 'deposit', 'wire_transfer']:
            prices[p] = contado_price

        normal_price = soup.find('span', 'precio').find('b')
        normal_price = Decimal(clean_price_string(normal_price.string))

        for p in ['dated_check', 'credit_card', 'debit_card', 'presto_card',
                  'ripley_card']:
            prices[p] = normal_price

        return name, prices

    @classmethod
    def _product_urls_and_types(cls, product_types):
        browser = mechanize.Browser()

        categories = [
            ['75', 'Notebook'],
            ['83', 'VideoCard'],
            ['61', 'Processor'],
            ['61', 'Processor'],
            ['73', 'Monitor'],
            ['60', 'Motherboard'],
            ['72', 'Ram'],
            ['62', 'StorageDrive'],
            ['70', 'PowerSupply'],
        ]

        sub_category_urls = []

        for category, ptype in categories:
            if ptype not in product_types:
                continue
            url = 'http://www.pc-express.cl/index.php?cPath=' + category
            soup = BeautifulSoup(browser.open(url).get_data())

            sub_category_containers = soup.findAll('div', 'subcategorias')

            for container in sub_category_containers:
                url = container.find('a')['href']
                sub_category_urls.append([url, ptype])

        product_links = []

        for url, ptype in sub_category_urls:
            if ptype not in product_types:
                continue
            soup = BeautifulSoup(browser.open(url).get_data())

            td_products = soup.findAll('td', 'wrapper_pic_br wrapper_pic_td')

            for td_product in td_products:
                link = td_product.find('a')['href']
                product_links.append([link, ptype])

        return product_links
