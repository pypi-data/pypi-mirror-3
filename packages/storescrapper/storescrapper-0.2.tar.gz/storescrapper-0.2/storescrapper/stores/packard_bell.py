from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class PackardBell(Store):
    @classmethod
    def product_types(cls):
        return [
            'Notebook',
        ]

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()
        product_data = browser.open(url).get_data()
        soup = BeautifulSoup(product_data)

        name = soup.find('div', {'class': 'tit_prod_det'}).string
        name = name.encode('ascii', 'ignore').strip()

        if not int(soup.find('span', {'class': 'unidades'}).string):
            return name, {}

        price = soup.find('div', {'class': 'precio_det'}).contents[1]
        price = Decimal(clean_price_string(price))

        prices = {}
        for p in ['cash', 'debit_card', 'credit_card']:
            prices[p] = price

        return name, prices

    @classmethod
    def _product_urls_and_types(cls, product_types):
        browser = mechanize.Browser()

        url_extensions = [
            ['116-Netbook.html', 'Notebook'],
            ['112-Notebook.html', 'Notebook'],
        ]

        product_links = []
        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue
            url = 'http://www.packardbell.cl/2012/catalogo/' + url_extension
            soup = BeautifulSoup(browser.open(url).get_data())
            imgs = soup.findAll('div', {'class': 'img_prod'})

            for img in imgs:
                l = img['onclick'].replace('javascript:location.href=\'', '')
                l = l.replace('\'', '')
                product_links.append([l, ptype])

        return product_links
