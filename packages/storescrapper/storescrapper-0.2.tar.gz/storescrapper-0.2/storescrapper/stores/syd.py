from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class Syd(Store):
    @classmethod
    def product_types(cls):
        return [
            'Notebook',
            'Monitor',
            'Ram',
        ]

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()
        soup = BeautifulSoup(browser.open(url).get_data())

        name = soup.findAll('h2')[5].string.encode('ascii', 'ignore')

        prices = {}

        try:
            price = soup.find('div', {'class': 'detallesCompra'})
            price = price.findAll('dd')[1].string
            price = Decimal(clean_price_string(price))
        except Exception:
            return name, None

        for p in ['cash', 'debit_card', 'credit_card']:
            prices[p] = price

        return name, prices

    @classmethod
    def _product_urls_and_types(cls, product_types):
        url_base = 'http://www.syd.cl'
        browser = mechanize.Browser()

        url_extensions = [
            ['/computadoras/macbook_pro', 'Notebook'],
            ['/computadoras/macbook_air', 'Notebook'],
            ['/computadoras/monitores', 'Monitor'],
            ['/memorias', 'Ram'],
        ]

        product_links = []
        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue

            url = url_base + url_extension + '/?op=all&crit='

            baseSoup = BeautifulSoup(browser.open(url).get_data())

            titles = baseSoup.findAll('h4')

            for title in titles:
                link = title.find('a')
                link = url_base + url_extension + '/' + link['href']
                product_links.append([link, ptype])

        return product_links
