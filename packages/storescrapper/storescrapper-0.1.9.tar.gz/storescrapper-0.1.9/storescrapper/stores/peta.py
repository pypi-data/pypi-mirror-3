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

        try:
            avail = soup.find('p', {'class': 'availability in-stock'})
            avail = avail.find('span')
            if avail.string and avail.string != 'En existencia':
                return name, None
        except Exception:
            return name, None

        try:
            price = soup.find('span', {'class': 'price'}).string.split('$')[1]
            price = Decimal(clean_price_string(price))
        except Exception:
            return name, None

        return name, price

    @classmethod
    def _product_urls_and_types(cls, product_types):
        browser = mechanize.Browser()

        url_extensions = [
            ['computadores-1/netbooks.html', 'Notebook'],
            ['computadores-1/notebooks.html', 'Notebook'],
            ['computadores-1/apple.html?appletype=898,903', 'Notebook'],
            ['peta-cl/tarjetas-de-video.html', 'VideoCard'],
            ['peta-cl/procesadores.html', 'Processor'],
            ['peta-cl/monitores.html', 'Monitor'],
            ['audio-y-video-1/televisores.html', 'Television'],
            ['peta-cl/placas-madre-1.html', 'Motherboard'],
            ['partes-y-piezas/memorias.html', 'Ram'],
            ['partes-y-piezas/discos-duros.html', 'StorageDrive'],
            ['partes-y-piezas/fuentes-de-poder.html', 'PowerSupply'],
        ]

        product_links = []
        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue

            url = 'http://www.peta.cl/' + url_extension
            first_page_url = url + '?limit=36&p=1'

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
