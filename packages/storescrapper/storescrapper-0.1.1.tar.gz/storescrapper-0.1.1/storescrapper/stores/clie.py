from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class Clie(Store):

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()
        product_data = browser.open(url).get_data()
        product_soup = BeautifulSoup(product_data)

        availability_text = product_soup.findAll('td',
                {'class': 'texto-neg-bold'})[-1].find('a').string.strip()
        if availability_text[0] == '0':
            return None

        product_name = product_soup.find('td', {'class': 'tit-nar-bold'})
        product_name = product_name.contents[0].split('&#8226;')[0]
        product_name = product_name.replace('&nbsp;&raquo; ', '').strip()

        product_price = product_soup.find('td',
                {'background': 'images/ficha/bg_efectivo_d.gif'})
        product_price = Decimal(clean_price_string(
            product_price.find('a').string))

        if not product_price:
            return None

        return [product_name, product_price]

    @classmethod
    def _product_urls_and_types(cls, product_types):
        url_base = 'http://www.clie.cl/'
        browser = mechanize.Browser()

        url_extensions = [
            ['561', 'Notebook'],
            ['542', 'Notebook'],
            ['580', 'Notebook'],
            ['564', 'Notebook'],
            ['581', 'Notebook'],
            ['562', 'Notebook'],
            ['579', 'Notebook'],
            ['575', 'Notebook'],
            ['612', 'Notebook'],
            ['598', 'Notebook'],
            ['596', 'Notebook'],
            ['595', 'Notebook'],
            ['178', 'Notebook'],
            ['500', 'Notebook'],
            ['158', 'Notebook'],
            ['307', 'Notebook'],
            ['308', 'Notebook'],
            ['646', 'Processor'],
            ['167', 'Screen'],
            ['551', 'Screen'],
            ['19', 'Screen'],
            ['536', 'Screen'],
            ['156', 'Screen'],
            ['310', 'Screen'],
            ['266', 'Screen'],
            ['550', 'Screen'],
            ['560', 'Screen'],
            ['632', 'Screen'],
            ['616', 'Screen'],
            ['614', 'Screen'],
            ['26', 'Ram'],
            ['446', 'Ram'],
            ['438', 'StorageDrive'],
            ['434', 'StorageDrive'],
            ['738', 'StorageDrive'],
            ['642', 'StorageDrive'],
        ]

        product_links = []

        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue
            num_page = 1
            while True:
                url_webpage = url_base + '?ver=4&categoria_producto=' + \
                              url_extension + '&pagina=' + str(num_page)

                base_soup = BeautifulSoup(browser.open(url_webpage).get_data())
                product_cells = base_soup.findAll('td', {'colspan': '2'})[1:]

                if not product_cells:
                    break

                for product_cell in product_cells:
                    link = product_cell.find('a')
                    url = link['onclick'].split('\'')[1]
                    product_links.append([url_base + url, ptype])

                num_page += 1

        return product_links
