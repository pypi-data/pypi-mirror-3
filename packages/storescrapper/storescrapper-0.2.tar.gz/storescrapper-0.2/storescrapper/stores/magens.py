from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class Magens(Store):
    @classmethod
    def product_types(cls):
        return [
            'Notebook',
            'VideoCard',
            'Processor',
            'Monitor',
            'Television',
            'Motherboard',
            'Ram',
            'StorageDrive',
            'PowerSupply'
        ]

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()
        product_data = browser.open(url).get_data()
        product_soup = BeautifulSoup(product_data)

        name = product_soup.find('div', {'class': 'titleContent'}).string
        name = name.encode('ascii', 'ignore')

        try:
            availability = product_soup.find('div', {'class': 'stock'})
            availability = availability.contents[4]
        except AttributeError:
            return name, {}

        if 'Agotado' in availability:
            return name, {}

        prices = {}

        cash_price = product_soup.findAll('div', {'class': 'precioDetalle'})[1]
        cash_price = cash_price.string.split('$')[1]
        cash_price = Decimal(clean_price_string(cash_price))

        for p in ['cash', 'deposit', 'wire_transfer']:
            prices[p] = cash_price

        normal_price = product_soup.find('div', 'precioDetalle')
        normal_price = normal_price.string.split('$')[1]
        normal_price = Decimal(clean_price_string(normal_price))

        for p in ['debit_card', 'credit_card', 'check']:
            prices[p] = normal_price

        return name, prices

    @classmethod
    def _product_urls_and_types(cls, product_types):
        browser = mechanize.Browser()

        url_extensions = [
            ['notebooks-netbooks-netbooks-11-c-15_199.html', 'Notebook'],
            ['notebooks-netbooks-notebooks-12-13-c-15_202.html', 'Notebook'],
            ['notebooks-netbooks-notebooks-14-c-15_203.html', 'Notebook'],
            ['notebooks-netbooks-notebooks-15-c-15_204.html', 'Notebook'],
            ['notebooks-netbooks-notebooks-16-mas-c-15_205.html', 'Notebook'],
            ['video-pcie-ati-c-24_130.html', 'VideoCard'],
            ['video-pcie-nvidia-c-24_129.html', 'VideoCard'],
            ['video-profesionales-c-24_131.html', 'VideoCard'],
            ['promo-nvidia-c-24_275.html', 'VideoCard'],
            ['cpu-amd-am3-c-1_302.html', 'Processor'],
            ['cpu-amd-sam3-c-1_31.html', 'Processor'],
            ['cpu-fm1-c-1_441.html', 'Processor'],
            ['cpu-intel-s1156-c-1_197.html', 'Processor'],
            ['cpu-intel-s775-c-1_32.html', 'Processor'],
            ['cpu-server-c-1_30.html', 'Processor'],
            ['monitores-lcd-c-13_90.html', 'Monitor'],
            ['monitores-led-c-13_200.html', 'Monitor'],
            ['televisores-lcdtv-c-13_91.html', 'Television'],
            ['televisores-ledtv-c-13_210.html', 'Television'],
            ['placas-madre-c-2.html', 'Motherboard'],
            ['memorias-c-12.html', 'Ram'],
            ['discos-duros-c-3_35.html', 'StorageDrive'],
            ['discos-notebook-c-3_37.html', 'StorageDrive'],
            ['ssd-c-3_215.html', 'StorageDrive'],
            ['fuentes-poder-c-10_76.html', 'PowerSupply'],
        ]

        product_links = []
        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue
            url = 'http://www.magens.cl/catalog/' + url_extension + \
                  '?mostrar=1000'
            soup = BeautifulSoup(browser.open(url).get_data())

            product_containers = soup.findAll('div',
                    {'class': 'text11 uppercase tituloProducto'})
            for container in product_containers:
                link = container.find('a')['href']
                product_links.append([link.split('?osCsid')[0], ptype])

        return product_links
