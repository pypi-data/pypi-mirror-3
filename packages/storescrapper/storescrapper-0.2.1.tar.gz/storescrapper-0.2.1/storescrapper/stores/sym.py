from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class Sym(Store):
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
            'PowerSupply',
            'ComputerCase'
        ]

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()
        soup = BeautifulSoup(browser.open(url).get_data())

        stock_status = soup.find('li', 'stocks')
        stock_status = stock_status.findAll('span')[1].contents[0]

        title_span = soup.find('h1')
        title = str(title_span.string).strip()

        if 'pedido' not in stock_status and 'stock' not in stock_status:
            return [title, {}]

        prices = {}

        price_container = soup.find('span', 'red')
        price_string = price_container.find('strong').string
        cash_price = Decimal(clean_price_string(price_string))

        for p in ['cash', 'deposit', 'wire_transfer']:
            prices[p] = cash_price

        containers = soup.find('div', {'id': 'product-info'}).findAll('li')

        offset = 0
        try:
            if containers[0]['class'] == 'li_ahorro':
                offset = 1
        except KeyError:
            pass

        check_price = Decimal(clean_price_string(containers[offset
            + 1].contents[1]))

        prices['check'] = check_price

        debit_price = Decimal(clean_price_string(containers[offset
            + 2].contents[1]))

        prices['debit_card'] = debit_price

        normal_price = Decimal(clean_price_string(containers[offset
            + 3].contents[1]))

        for p in ['dated_check', 'credit_card', 'presto_card', 'ripley_card']:
            prices[p] = normal_price

        return title, prices

    @classmethod
    def _product_urls_and_types(cls, product_types):
        browser = mechanize.Browser()

        url_extensions = [
            ['?cat=104', 'Notebook'],         # Notebooks
            ['?cat=32_68', 'VideoCard'],      # Tarjetas de video AGP
            ['?cat=32_69', 'VideoCard'],      # Tarjetas de video PCIe
            ['?cat=50', 'Processor'],         # Procesadores Intel
            ['?cat=25', 'Processor'],         # Procesadores AMD
            ['?cat=81', 'Monitor'],           # Monitores LCD
            ['?cat=26', 'Motherboard'],       # MB AMD
            ['?cat=49', 'Motherboard'],       # MB Intel
            ['?cat=27', 'Ram'],               # RAM
            ['?cat=29_61', 'StorageDrive'],   # HDD Notebook
            ['?cat=29_62', 'StorageDrive'],   # HDD SATA
            ['?cat=29_129', 'StorageDrive'],  # SSD
            ['?cat=40', 'PowerSupply'],       # Fuentes de poder
            ['?cat=39', 'ComputerCase'],      # Gabinetes
        ]

        product_urls_and_types = {}

        for url_extension, product_type in url_extensions:
            if product_type not in product_types:
                continue

            page_number = 1

            while True:
                url_webpage = 'http://www.sym.cl/%s&page=%d' % \
                             (url_extension, page_number)

                base_data = browser.open(url_webpage).get_data()
                base_soup = BeautifulSoup(base_data)

                link_containers = base_soup.findAll('div',
                        'listadoindiv')

                if not link_containers:
                    break

                break_flag = False

                for link_container in link_containers:
                    url = link_container.find('h2').find('a')['href']
                    if url in product_urls_and_types:
                        break_flag = True
                        break
                    product_urls_and_types[url] = product_type

                if break_flag:
                    break

                page_number += 1

        return product_urls_and_types.items()
