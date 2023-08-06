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
            'PowerSupply',
            'ComputerCase'
        ]

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()
        product_data = browser.open(url).get_data()
        soup = BeautifulSoup(product_data)

        name = soup.find('h1').string.encode('ascii', 'ignore').strip()

        try:
            normal_price = Decimal(clean_price_string(
                soup.find('span', 'price').string))
        except AttributeError:
            return [name, {}]

        prices = {}

        for p in ['debit_card', 'credit_card', 'check']:
            prices[p] = normal_price

        cash_price = Decimal(int(int(normal_price) * 0.97))

        for p in ['cash', 'deposit', 'wire_transfer']:
            prices[p] = cash_price

        return name, prices

    @classmethod
    def _product_urls_and_types(cls, product_types):
        browser = mechanize.Browser()

        url_extensions = [
            ['computadores/moviles/notebooks.html', 'Notebook'],
            ['computadores/moviles/netbooks.html', 'Notebook'],
            ['computadores/moviles/ultrabooks.html', 'Notebook'],
            ['apple.html', 'Notebook'],
            ['partes-y-piezas/display/tarjetas-de-video.html', 'VideoCard'],
            ['partes-y-piezas/componentes/procesadores.html', 'Processor'],
            ['partes-y-piezas/display/monitores.html', 'Monitor'],
            ['partes-y-piezas/componentes/placas-madre.html', 'Motherboard'],
            ['partes-y-piezas/almacenamiento/memorias.html', 'Ram'],
            ['partes-y-piezas/almacenamiento/discos-duros.html',
                'StorageDrive'],
            ['partes-y-piezas/componentes/fuentes-de-poder.html',
                'PowerSupply'],
            ['partes-y-piezas/componentes/gabinetes.html', 'ComputerCase'],
            ['audio-y-video/televisores.html', 'Television'],
        ]

        product_links = {}
        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue

            url = 'http://www.peta.cl/' + url_extension
            page_number = 1

            break_flag = False
            partial_links = {}

            while True:
                complete_url = url + '?limit=36&p=' + str(page_number)

                soup = BeautifulSoup(browser.open(complete_url).get_data())
                soup = soup.find('div', 'category-products')

                p_cells = []
                p_cells.extend(soup.findAll('li', {'class': 'item first'}))
                p_cells.extend(soup.findAll('li', {'class': 'item'}))
                p_cells.extend(soup.findAll('li', {'class': 'item last'}))

                for cell in p_cells:
                    link = cell.find('a')['href']
                    if link in partial_links:
                        break_flag = True
                        break
                    partial_links[link] = ptype

                if break_flag:
                    break
                page_number += 1

            product_links.update(partial_links)

        return product_links.items()
