from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class MacOnline(Store):
    @classmethod
    def product_types(cls):
        return [
            'Notebook',
            'Monitor',
        ]

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()
        product_data = browser.open(url).get_data()
        soup = BeautifulSoup(product_data)

        name = soup.findAll('h2')[1]
        name = name.string.strip().encode('ascii', 'ignore')

        price = soup.find('span', {'itemprop': 'price'}).contents[0]
        price = Decimal(clean_price_string(price))

        prices = {}
        for p in ['cash', 'credit_card', 'debit_card', 'wire_transfer']:
            prices[p] = price

        return name, prices

    @classmethod
    def _product_urls_and_types(cls, product_types):
        url_base = 'http://www.maconline.cl'
        browser = mechanize.Browser()
        product_links = []

        url_extensions = [
            ['397.html', 'Notebook'],
            ['421.html', 'Notebook'],
            ['513.html', 'Monitor'],
        ]

        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue
            page_number = 0
            while True:
                url = url_base + '/catalogo/' + url_extension + \
                      '?pagina=' + str(page_number)

                soup = BeautifulSoup(browser.open(url).get_data())
                cells = soup.findAll('td', 'dd')

                if not cells:
                    break

                for cell in cells:
                    link = url_base + cell.find('a')['href']
                    product_links.append([link, ptype])
                page_number += 1

        return product_links
