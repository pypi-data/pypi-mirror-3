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
            'StorageDrive'
        ]

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()
        product_data = browser.open(url).get_data()
        soup = BeautifulSoup(product_data)

        name = soup.find('td', {'class': 'tit_categoria_despliegue'})
        name = name.contents[0].strip().encode('ascii', 'ignore')

        price = soup.find('em').string.split('$')[1]
        price = Decimal(clean_price_string(price))

        return name, price

    @classmethod
    def _product_urls_and_types(cls, product_types):
        url_base = 'http://www.maconline.cl'
        browser = mechanize.Browser()
        product_links = []

        url_extensions = [
            ['397.html', 'Notebook'],
            ['421.html', 'Notebook'],
            ['384.html', 'Notebook'],
            ['288.html', 'Monitor'],
            ['435.html', 'Notebook'],
            ['293', 'StorageDrive'],
        ]

        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue
            page_number = 0
            while True:
                url = url_base + '/catalogo/' + url_extension + \
                      '?pagina=' + str(page_number)

                soup = BeautifulSoup(browser.open(url).get_data())
                titles = soup.findAll('td', {'class': 'nombre_producto'})

                if not titles:
                    break

                for i in range(len(titles)):
                    link = url_base + titles[i].find('a')['href']
                    if link in product_links:
                        continue
                    product_links.append([link, ptype])
                page_number += 1

        return product_links
