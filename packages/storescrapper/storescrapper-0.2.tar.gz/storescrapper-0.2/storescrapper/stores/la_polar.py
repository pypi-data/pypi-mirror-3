from decimal import Decimal
import json
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class LaPolar(Store):
    @classmethod
    def product_types(cls):
        return [
            'Notebook',
            'Television'
        ]

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()
        product_data = browser.open(url).get_data()
        soup = BeautifulSoup(product_data)

        name = soup.find('div', {'class': 'LetraDetalleProducto'})
        name = name.string.encode('ascii', 'ignore')

        price = soup.findAll('span', {'class': 'PrecioDetalleRojo'})[1]
        price = price.string.split('$')[1]
        price = Decimal(clean_price_string(price))

        prices = {}
        for p in ['cash', 'debit_card', 'credit_card', 'lapolar_card']:
            prices[p] = price

        return [name, prices]

    @classmethod
    def _product_urls_and_types(cls, product_types):
        extensions = [
            ['electronica/computacion/notebook/', 'Notebook'],
            ['electronica/computacion/netbook/', 'Notebook'],
            ['electrohogar/tv_video/led/', 'Television'],
            ['electrohogar/tv_video/lcd/', 'Television'],
        ]

        browser = mechanize.Browser()

        products_data = []
        for extension, ptype in extensions:
            if ptype not in product_types:
                continue
            page = 1
            while True:
                url = 'http://www.lapolar.cl/internet/catalogo/listados/' + \
                      extension + str(page)
                baseSoup = BeautifulSoup(browser.open(url).get_data())

                try:
                    data = baseSoup.findAll('script')[-3].string.strip()
                    data = data.replace('var listado_productos_json = ', '')
                    data = json.loads(data[:-1])
                except ValueError:
                    break

                json_product_array_data = []

                for row in data['lista_completa']:
                    json_product_array_data.extend(row['sub_lista'])

                for json_product_data in json_product_array_data:
                    product_id = json_product_data['prid']

                    url = 'http://www.lapolar.cl/internet/catalogo/detalles/' \
                          '%s%s' % (extension, product_id)

                    products_data.append([url, ptype])

                page += 1

        return products_data
