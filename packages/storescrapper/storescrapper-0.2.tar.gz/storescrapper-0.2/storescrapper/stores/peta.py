from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class Peta(Store):
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

        name = soup.find('h1', {'class': 'p-title'}).string
        name = name.encode('ascii', 'ignore')

        prices = {}

        cash_price = soup.find('span', 'price').string.split('$')[1]
        cash_price = Decimal(clean_price_string(cash_price))

        for p in ['cash', 'deposit', 'wire_transfer', 'check']:
            prices[p] = cash_price

        normal_price = soup.findAll('span', 'price')[1].string.split('$')[1]
        normal_price = Decimal(clean_price_string(normal_price))

        for p in ['debit_card', 'credit_card']:
            prices[p] = normal_price

        return name, prices

    @classmethod
    def _product_urls_and_types(cls, product_types):
        browser = mechanize.Browser()

        url_extensions = [
            ['computadores-1/netbooks.html', 'Notebook'],
            ['computadores-1/notebooks.html', 'Notebook'],
            ['computadores-1/ultrabooks.html', 'Notebook'],
            ['apple-1.html', 'Notebook'],
            ['partes-y-piezas/tarjetas-de-video.html', 'VideoCard'],
            ['partes-y-piezas/procesadores.html', 'Processor'],
            ['partes-y-piezas/monitores.html', 'Monitor'],
            ['partes-y-piezas/placas-madre.html', 'Motherboard'],
            ['partes-y-piezas/memorias.html', 'Ram'],
            ['partes-y-piezas/discos-duros.html', 'StorageDrive'],
            ['partes-y-piezas/fuentes-de-poder.html', 'PowerSupply'],
            ['audio-y-video-1/televisores.html', 'Television'],
        ]

        product_links = []
        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue

            url = 'http://www.peta.cl/' + url_extension
            first_page_url = url + '?limit=36&p=1'

            print first_page_url

            soup = BeautifulSoup(browser.open(first_page_url).get_data())

            page_count = soup.find('div', {'class': 'pages'})
            if page_count:
                page_count = int(page_count.findAll('a')[-2].string)
            else:
                page_count = 1

            for page_number in range(page_count):
                page_number += 1
                complete_url = url + '?limit=36&p=' + str(page_number)

                soup = BeautifulSoup(browser.open(complete_url).get_data())
                soup = soup.find('div', 'category-products')

                p_cells = []
                p_cells.extend(soup.findAll('li', {'class': 'item first'}))
                p_cells.extend(soup.findAll('li', {'class': 'item'}))
                p_cells.extend(soup.findAll('li', {'class': 'item last'}))

                for cell in p_cells:
                    link = cell.find('a')['href']

                    product_links.append([link, ptype])

        return product_links
