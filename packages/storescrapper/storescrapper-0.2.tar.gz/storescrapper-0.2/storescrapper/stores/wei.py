from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class Wei(Store):
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
            ]

    @classmethod
    def _retrieve_product(cls, url):
        br = mechanize.Browser()
        soup = BeautifulSoup(br.open(url).get_data())

        availabilities = soup.find('table', {'class': 'pdisponibilidad'})
        availabilities = availabilities.findAll('td')

        name = soup.find('title').string.split('WEI CHILE S. A. - ')[1]

        for availability in availabilities:
            if 'Producto agotado' in availability.contents[1]:
                return name, {}

        prices = {}

        inet_price = soup.find('table', 'pprecio').find('h1').string
        inet_price = Decimal(clean_price_string(inet_price))

        for p in ['credit_card', 'check', 'cash', 'deposit', 'wire_transfer']:
            prices[p] = inet_price

        normal_price = soup.findAll('h5')[1].string
        normal_price = int(clean_price_string(normal_price))

        prices['debit_card'] = Decimal(int(round(normal_price * 0.97)))

        for p in ['dated_check', 'presto_card', 'ripley_card']:
            prices[p] = Decimal(normal_price)

        return name, prices

    @classmethod
    def _product_urls_and_types(cls, product_types):
        base_url = 'http://www.wei.cl/'
        browser = mechanize.Browser()

        category_urls = [
            ['252', 'Notebook'],      # Notebooks
            ['147', 'Notebook'],      # Netbook
            ['175', 'VideoCard'],     # Tarjetas de video AGP
            ['176', 'VideoCard'],     # Tarjetas de video PCI Express
            ['119', 'Processor'],     # Procesadores AMD
            ['120', 'Processor'],     # Procesadores Intel
            ['205', 'Television'],    # LCD TV
            ['80', 'Monitor'],     # Monitores LCD
            ['65', 'Motherboard'],     # MB AMD
            ['84', 'Motherboard'],     # MB Intel
            ['68', 'Ram'],     # RAM Notebook
            ['89', 'Ram'],     # RAM DDR
            ['195', 'Ram'],     # RAM DDR2
            ['199', 'Ram'],     # RAM DDR3
            ['70', 'StorageDrive'],     # HDD IDE
            ['71', 'StorageDrive'],     # HDD SATA
            ['78', 'StorageDrive'],     # HDD Notebook
            ['9', 'PowerSupply'],     # Fuentes de poder
        ]

        product_links = {}
        for category_url, ptype in category_urls:
            if ptype not in product_types:
                continue
            desde = 1
            while True:
                url = base_url + 'index.htm?op=categoria&ccode=' + \
                      category_url + '&desde=' + str(desde)

                soup = BeautifulSoup(browser.open(url).get_data())

                product_cells = soup.findAll('div', {'class': 'box1'})
                flag = False

                if not product_cells:
                    break

                for cell in product_cells:
                    link = base_url + cell.parent['href']
                    if link in product_links:
                        flag = True
                        break
                    product_links[link] = ptype

                if flag:
                    break

                desde += 20

        return product_links.items()
