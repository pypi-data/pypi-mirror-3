from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class Clie(Store):
    @classmethod
    def product_types(cls):
        return [
            'Notebook',
            'Processor',
            'Monitor',
            'Television',
            'Ram',
            'StorageDrive'
        ]

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()
        product_data = browser.open(url).get_data()
        product_soup = BeautifulSoup(product_data)

        product_name = product_soup.find('td', {'class': 'tit-nar-bold'})
        product_name = product_name.contents[0].split('&#8226;')[0]
        product_name = product_name.replace('&nbsp;&raquo; ', '').strip()

        prices = {}

        cash_product_price = product_soup.find('td',
                {'background': 'images/ficha/bg_efectivo_d.gif'})
        cash_product_price = Decimal(clean_price_string(
            cash_product_price.find('a').string))
        for p in ['cash', 'deposit', 'wire_transfer']:
            prices[p] = cash_product_price

        normal_product_price = product_soup.find('td',
                {'background': 'images/ficha/bg_precio_normal_d.gif'})
        normal_product_price = Decimal(clean_price_string(
            normal_product_price.find('a').string))
        for p in ['debit_card', 'credit_card']:
            prices[p] = normal_product_price

        return [product_name, prices]

    @classmethod
    def _product_urls_and_types(cls, product_types):
        url_base = 'http://www.clie.cl/'
        browser = mechanize.Browser()

        category_codes = [
            ['157', 'Notebook'],        # Notebooks
            ['433', 'StorageDrive'],    # PC HDDs
            ['275', 'StorageDrive'],    # Notebook HDDs
            ['25', 'Ram'],              # PC Ram
            ['25', 'Ram'],              # PC Ram
            ['392', 'Ram'],             # Notebook Ram
            ['615', 'Monitor'],         # LED Monitor
            ['18', 'Monitor'],          # LCD Monitor
            ['265', 'Television'],      # LCD Television
            ['613', 'Television'],      # LED Television
            ['645', 'Processor'],       # Processors
        ]

        product_links = []

        product_pages_urls = []

        for code, ptype in category_codes:
            if ptype not in product_types:
                continue

            category_url = 'http://www.clie.cl/?categoria=' + code
            soup = BeautifulSoup(browser.open(category_url).get_data())

            brands_table = soup.find('table', {'width': '150'})
            brand_links = brands_table.findAll('a', {'id': 'ocultar'})

            for link in brand_links:
                complete_url = 'http://www.clie.cl/' + link['href']
                product_pages_urls.append([complete_url, ptype])

        manual_brand_urls = [
            # HP Netbooks
            ['http://www.clie.cl/?categoria_producto=561&categoria=&ver=4',
             'Notebook'],
            # Toshiba Netbooks
            ['http://www.clie.cl/?categoria_producto=564&categoria=&ver=4',
             'Notebook'],
            # Acer Netbooks
            ['http://www.clie.cl/?categoria_producto=562&categoria=&ver=4',
             'Notebook'],
            # Lenovo Netbooks
            ['http://www.clie.cl/?categoria_producto=579&categoria=&ver=4',
             'Notebook'],
            # Apple Macbook Air
            ['http://www.clie.cl/?categoria_producto=726&categoria=0&ver=4',
             'Notebook'],
            # Apple Macbook Pro
            ['http://www.clie.cl/?categoria_producto=725&categoria=0&ver=4',
             'Notebook'],
        ]

        product_pages_urls.extend(manual_brand_urls)

        for page_url, ptype in product_pages_urls:
            if ptype not in product_types:
                continue

            num_page = 1
            while True:
                url_webpage = page_url + '&pagina=' + str(num_page)

                soup = BeautifulSoup(browser.open(url_webpage).get_data())
                product_cells = soup.findAll('td', {'colspan': '2'})[1:]

                if not product_cells:
                    break

                for product_cell in product_cells:
                    link = product_cell.find('a')
                    url = link['onclick'].split('\'')[1]
                    product_links.append([url_base + url, ptype])

                num_page += 1

        return product_links
