from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class HpOnline(Store):
    @classmethod
    def product_types(cls):
        return [
            'Notebook',
        ]

    @classmethod
    def _retrieve_product(cls, url):
        br = mechanize.Browser()

        # Double open URL because the first redirects to home and sets a cookie
        BeautifulSoup(br.open(url).get_data())
        product_soup = BeautifulSoup(br.open(url).get_data())

        product_name = product_soup.findAll('h2')[-1].string
        product_name = product_name.encode('ascii', 'ignore')

        product_price = product_soup.find('h1', {'class': 'bigtitle'})
        product_price = product_price.contents[0].split('$')[1]
        product_price = Decimal(clean_price_string(product_price))

        prices = {}
        for p in ['debit_card', 'credit_card']:
            prices[p] = product_price

        return [product_name, prices]

    @classmethod
    def _product_urls_and_types(cls, product_types):
        url_base = 'http://www.hponline.cl'

        browser = mechanize.Browser()

        url_extensions = [
            ['categoria.aspx?cat=ZA==&V=G', 'Notebook'],
        ]

        product_links = []
        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue
            url = url_base + '/personas/' + url_extension

            soup = BeautifulSoup(browser.open(url).get_data())
            product_cells = soup.findAll('div', {'class': 'product'})

            for cell in product_cells:
                elem = [url_base + cell.find('a')['href'],
                        ptype]
                product_links.append(elem)

        return product_links
