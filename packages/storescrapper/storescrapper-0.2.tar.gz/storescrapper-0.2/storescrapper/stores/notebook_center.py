from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class NotebookCenter(Store):
    @classmethod
    def product_types(cls):
        return [
            'Notebook',
            'Processor',
            'Monitor',
            'Television',
            'Ram',
            'StorageDrive',
        ]

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()
        product_data = browser.open(url).get_data()
        soup = BeautifulSoup(product_data)

        prices = {}

        name = soup.find('span', 'titulo_producto').string
        name = name.encode('ascii', 'ignore')

        cash_price = soup.find('span', 'precio_producto_efectivo')
        cash_price = Decimal(clean_price_string(cash_price.string))

        prices['cash'] = cash_price

        normal_price = soup.find('span', 'otro_precio')
        if normal_price:
            normal_price = normal_price.string.split('$')[1]
            normal_price = Decimal(clean_price_string(normal_price))
        else:
            normal_price = cash_price

        for p in ['credit_card', 'debit_card', 'wire_transfer']:
            prices[p] = normal_price

        return name, prices

    @classmethod
    def _product_urls_and_types(cls, product_types):
        url_base = 'http://www.notebookcenter.cl/'
        browser = mechanize.Browser()

        url_extensions = [
            ['565', 'Notebook'],  # Macbook Air
            ['558', 'Notebook'],  # Macbook Pro
            ['61', 'Notebook'],   # Notebook Acer
            ['251', 'Notebook'],  # Notebook Dell
            ['57', 'Notebook'],   # Notebook HP
            ['64', 'Notebook'],   # Notebook Lenovo
            ['418', 'Notebook'],  # Netbook Samsung
            ['212', 'Notebook'],  # Notebook Sony
            ['63', 'Notebook'],   # Notebook Toshiba
            ['603', 'Notebook'],   # Notebook Corporativo Acer
            ['602', 'Notebook'],   # Notebook Corporativo Lenovo
            ['598', 'Notebook'],   # Notebook Corporativo HP
            ['606', 'Notebook'],   # Notebook Corporativo Dell
            ['401', 'Notebook'],  # Netbook Acer
            ['402', 'Notebook'],  # Netbook Dell
            ['406', 'Notebook'],  # Netbook Samsung
            ['472', 'Processor'],  # Procesadores AMD
            ['473', 'Processor'],  # Procesadores Intel
            ['275', 'Monitor'],  # Monitores Apple
            ['162', 'Monitor'],  # Monitores LCD
            ['640', 'Monitor'],  # Monitores LED
            ['323', 'Television'],  # Televisor LCD
            ['641', 'Television'],  # Televisor LED
            ['6', 'Ram'],  # Notebook RAM
            ['109', 'StorageDrive'],  # HDD Notebook
            ['412', 'StorageDrive'],  # HDD Desktop
        ]

        product_links = []
        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue

            index = 0
            while True:
                url = url_base + '?p=1&op=2&p3=' + url_extension + '&i_p=' + \
                      str(index)

                soup = BeautifulSoup(browser.open(url).get_data())

                product_containers = soup.findAll('div',
                        {'id': 'producto_inicio'})
                if not product_containers:
                    break

                for product_container in product_containers:
                    js_data = product_container.find('a')['href']

                    js_ars = [int(s) for s in js_data.replace("'", ' ').split()
                              if s.isdigit()]
                    id_prod = js_ars[2]
                    link = url_base + '?p=2&op=1&i_p=' + str(id_prod)
                    product_links.append([link, ptype])

                index += 1

        return product_links
