from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class Paris(Store):
    @classmethod
    def product_types(cls):
        return [
            'Notebook',
            'Television',
        ]

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()
        product_data = browser.open(url).get_data()
        soup = BeautifulSoup(product_data)

        name = soup.find('div', {'id': 'ficha-producto-nombre'}).string
        name = name.encode('ascii', 'ignore').strip()

        prices = []

        try:
            price = soup.find('div', {'id': 'ficha-producto-precio'})
            price = price.string.split('$')[1]
            price = Decimal(clean_price_string(price))
            prices.append(price)
        except Exception:
            pass

        try:
            price = soup.find('div', {'id': 'ficha-producto-precio-normal'})
            price = price.string.split('$')[1]
            price = Decimal(clean_price_string(price))
            prices.append(price)
        except Exception:
            pass

        if not prices:
            raise Exception

        price = min(prices)

        return name, price

    @classmethod
    def _product_urls_and_types(cls, product_types):
        browser = mechanize.Browser()

        urls = [
            # Notebooks
            ['http://www.paris.cl/webapp/wcs/stores/servlet/'
             'categoryTodos_10001_40000000577_-5_51145648_18877035_si_2__'
             '18877035,50999203,51145648_', 'Notebook'],
            # Netbooks
            ['http://www.paris.cl/webapp/wcs/stores/servlet/'
             'category_10001_40000000577_-5_51056269_18877035_51039699_'
             '18877035,51039699,51056269', 'Notebook'],
            # LCD
            ['http://www.paris.cl/webapp/wcs/stores/servlet/categoryTodos_'
             '10001_40000000577_-5_51056211_20096521_si_2__20096521,51056194,'
             '51056196,51056211_', 'Television'],
            ]

        product_links = []
        for url, ptype in urls:
            if ptype not in product_types:
                continue

            base_data = unicode(browser.open(url).get_data(), errors='ignore')
            soup = BeautifulSoup(base_data)

            link_divs = soup.findAll('div', {'class': 'descP2011'})

            for div in link_divs:
                linkId = int(div.find('a')['id'].replace('prod', '')) + 1

                link = 'http://www.paris.cl/webapp/wcs/stores/servlet/' \
                       'productLP_10001_40000000577_-5_51049202_18877035_' + \
                       str(linkId) + '_18877035,50999203,51049192,51049202__' \
                                     'listProd'

                product_links.append([link, ptype])

        return product_links
