from decimal import Decimal
import json
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class Entel(Store):
    @classmethod
    def product_types(cls):
        return [
            'Cell',
        ]

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()
        product_data = browser.open(url).get_data()

        soup = BeautifulSoup(product_data)

        product_title = soup.find('h1').contents[0].strip()
        product_title = product_title.encode('ascii', 'ignore')

        product_prices = []

        pricing_options_titles = soup.findAll('h3')
        for title in pricing_options_titles:
            if title.string in ['Pack Prepago', 'Compra equipo']:
                price_container = title.parent.find('span',
                        {'class': 'valorPrecio'})
                if price_container:
                    price = clean_price_string(price_container.string)
                    product_prices.append(Decimal(price))

        if product_prices:
            product_price = min(product_prices)
        else:
            product_price = 0

        prices = {}
        for p in ['cash', 'debit_card', 'credit_card']:
            prices[p] = product_price

        return [product_title, prices]

    @classmethod
    def _product_urls_and_types(cls, product_types):
        if 'Cell' not in product_types:
            return []

        url = 'http://personas.entelpcs.cl/PortalPersonas/com/entelpcs/' \
              'catalogoEquipos/publico/controllers/listadoEquipos/' \
              'ListadoEquiposController.jpf'

        browser = mechanize.Browser()
        product_links = []

        baseData = browser.open(url).get_data()
        json_data = json.loads(baseData, strict=False)

        json_products = json_data['equipos']
        for json_product in json_products:
            product_id = json_product['codProducto']
            product_links.append(['http://personas.entel.cl/PortalPersonas/' \
                                  'appmanager/entelpcs/personas?_nfpb=true&' \
                                  '_pageLabel=P12800364521294253893661&' \
                                  'codProducto=' + product_id, 'Cell'])

        return product_links
