from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class MyBox(Store):

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()
        product_data = browser.open(url).get_data()
        soup = BeautifulSoup(product_data)

        name = soup.find('h2').string
        price = soup.find('span', {'id': 'our_price_display'}).string
        price = Decimal(clean_price_string(price))

        return name, price

    @classmethod
    def _product_urls_and_types(cls, product_types):
        url_base = 'http://www.mybox.cl'
        browser = mechanize.Browser()

        url_extensions = [
            ['38-notebooks', 'Notebook'],
            ['7-monitores-y-proyectores', 'Monitor'],
            ['41-placas-madre', 'Motherboard'],
            ['44-procesadores', 'Processor'],
            ['54-tarjetas-de-video', 'VideoCard'],
            ['28-memoria-ram', 'Ram'],
            ['5-discos-duros', 'StorageDrive'],
            ['19-fuentes-de-poder', 'PowerSupply'],
        ]

        product_links = []
        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue
            url = url_base + '/' + url_extension + '?n=50'

            soup = BeautifulSoup(browser.open(url).get_data())
            prod_list = soup.find('ul', {'id': 'product_list'})

            if not prod_list:
                continue

            prod_cells = prod_list.findAll('li')

            for cell in prod_cells:
                entry = [url_base + cell.find('a')['href'], ptype]
                product_links.append(entry)

        return product_links
