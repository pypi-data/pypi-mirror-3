from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class PortatilChile(Store):
    @classmethod
    def product_types(cls):
        return [
            'Notebook',
        ]

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()
        product_data = browser.open(url).get_data()
        product_soup = BeautifulSoup(product_data)

        name = product_soup.find('th', {'colspan': '2'}).string
        name = name.encode('ascii', 'ignore').split('"')[1]

        price = product_soup.find('table', {'cellspacing': '1'}).find('table')
        price = price.findAll('td')[3].find('strong').string
        price = Decimal(clean_price_string(price))

        return name, price

    @classmethod
    def _product_urls_and_types(cls, product_types):
        if 'Notebook' not in product_types:
            return []

        urlBase = 'http://www.portatilchile.cl/productos.html'

        browser = mechanize.Browser()
        soup = BeautifulSoup(browser.open(urlBase).get_data())

        product_tables = soup.findAll('table', {'width': '226'})

        product_links = []

        for product_table in product_tables:
            link = product_table.find('a')['href']
            product_links.append([link, 'Notebook'])

        return product_links
