from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class Movistar(Store):
    @classmethod
    def product_types(cls):
        return [
            'Cell'
        ]

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()

        product_data = browser.open(url).get_data()

        soup = BeautifulSoup(product_data)
        name = soup.find('h2').string.encode('ascii', 'ignore')

        prepago_price_container = soup.find('li',
                {'class': 'pnormalForeverAlone'})

        if prepago_price_container:
            price = prepago_price_container.find('span').string
            price = Decimal(clean_price_string(price))
        else:
            price = Decimal(0)

        prices = {}
        for p in ['cash', 'debit_card', 'credit_card']:
            prices[p] = price

        return name, prices

    @classmethod
    def _product_urls_and_types(cls, product_types):
        browser = mechanize.Browser()

        if 'Cell' not in product_types:
            return []

        product_links = []
        page_number = 1
        while True:
            url = 'http://hogar.movistar.cl/equipos/index.php/catalogo' \
                  '/pagina/' + str(page_number)

            soup = BeautifulSoup(browser.open(url).get_data())

            prod_list = soup.findAll('div', {'class': 'producto'})

            if not prod_list:
                break

            for prod in prod_list:
                link = prod.find('a')['href']
                product_links.append([link, 'Cell'])

            page_number += 1

        return product_links
