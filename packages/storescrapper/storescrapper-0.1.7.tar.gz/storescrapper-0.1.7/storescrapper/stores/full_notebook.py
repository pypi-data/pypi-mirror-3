from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class FullNotebook(Store):

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()
        product_data = browser.open(url).get_data()
        product_soup = BeautifulSoup(product_data)

        product_name = product_soup.findAll('h2')[1].find('a').string
        product_name = product_name.encode('ascii', 'ignore')

        product_price = product_soup.find('span', {'id': 'esp'}).string
        product_price = Decimal(clean_price_string(product_price))

        return [product_name, product_price]

    @classmethod
    def _product_urls_and_types(cls, product_types):
        url_base = 'http://www.fullnotebook.cl/'
        url_buscar_productos = 'tienda/'

        browser = mechanize.Browser()

        product_links = []

        url_extensions = [
            ['notebooks', 'Notebook'],
            ['mini-notebooks', 'Notebook'],
            ['netbook', 'Notebook'],
        ]

        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue
            first_url = url_base + url_buscar_productos + url_extension + \
                        '/page/1'
            soup = BeautifulSoup(browser.open(first_url).get_data())

            lista_pags = soup.find('span', {'class': 'pages'})
            page_count = int(lista_pags.contents[0][-1])

            for i in range(page_count):
                page_url = url_base + url_buscar_productos + url_extension + \
                          '/page/' + str(i + 1)

                soup = BeautifulSoup(browser.open(page_url).get_data())

                for cont in soup.findAll('div', {'class': 'cliente'}):
                    elem = [cont.find('a')['href'].encode('ascii', 'ignore'),
                            ptype]
                    product_links.append(elem)

        return product_links
