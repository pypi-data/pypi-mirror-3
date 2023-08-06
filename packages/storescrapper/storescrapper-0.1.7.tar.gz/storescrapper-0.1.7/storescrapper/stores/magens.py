from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class Magens(Store):

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
            return name, None

        if 'Agotado' in availability:
            return name, None

        price = product_soup.findAll('div', {'class': 'precioDetalle'})[1]
        price = price.string.split('$')[1]
        price = Decimal(clean_price_string(price))

        return name, price

    @classmethod
    def _product_urls_and_types(cls, product_types):
        browser = mechanize.Browser()

        url_extensions = [
            ['notebooks-netbooks-netbooks-11-c-15_199.html', 'Notebook'],
            ['notebooks-netbooks-notebooks-12-13-c-15_202.html', 'Notebook'],
            ['notebooks-netbooks-notebooks-14-c-15_203.html', 'Notebook'],
            ['notebooks-netbooks-notebooks-15-c-15_204.html', 'Notebook'],
            ['notebooks-netbooks-notebooks-16-mas-c-15_205.html', 'Notebook'],
            ['video-c-24_128.html', 'VideoCard'],
            ['video-pcie-c-24_130.html', 'VideoCard'],
            ['video-pcie-nvidia-c-24_129.html', 'VideoCard'],
            ['video-profesionales-c-24_131.html', 'VideoCard'],
            ['sam2-c-1_196.html', 'Processor'],
            ['sam3-c-1_31.html', 'Processor'],
            ['intel-s1156-c-1_197.html', 'Processor'],
            ['intel-s775-c-1_32.html', 'Processor'],
            ['server-c-1_30.html', 'Processor'],
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
