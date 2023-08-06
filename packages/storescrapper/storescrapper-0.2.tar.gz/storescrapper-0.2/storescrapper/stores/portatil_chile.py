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

        prices = {}

        cash_price = product_soup.find('table',
                {'cellspacing': '1'}).find('table')
        cash_price = cash_price.findAll('td')[3].find('strong').string
        cash_price = Decimal(clean_price_string(cash_price))

        for p in ['cash', 'deposit', 'wire_transfer']:
            prices[p] = cash_price

        normal_price = product_soup.find('table',
                {'cellspacing': '1'}).find('table')
        normal_price = normal_price.findAll('td')[5].find('strong').string
        normal_price = Decimal(clean_price_string(normal_price))

        for p in ['debit_card', 'credit_card']:
            prices[p] = normal_price

        return name, prices

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
