from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class PcFactory(Store):
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
        soup = BeautifulSoup(browser.open(url).get_data())

        name_container = soup.find('span', {'class': 'men_confirmacion'})
        name = name_container.string.encode('ascii', 'ignore').strip()

        price = soup.find('span',
                {'class': 'texto_Precio_Oferta_Internet_BIG'})
        price = Decimal(clean_price_string(price.string))

        return name, price

    @classmethod
    def _product_urls_and_types(cls, product_types):
        url_base = 'http://www.pcfactory.cl'

        browser = mechanize.Browser()

        url_extensions = [
            ['?papa=24&categoria=424', 'Notebook'],   # Notebooks 7 a 11
            ['?papa=24&categoria=449', 'Notebook'],   # Notebooks 12 a 13
            ['?papa=24&categoria=410', 'Notebook'],   # Notebooks 14
            ['?papa=24&categoria=437', 'Notebook'],   # Notebooks 15
            ['?papa=24&categoria=436', 'Notebook'],   # Notebooks 16 y +
            ['?papa=334&categoria=40', 'VideoCard'],   # VGA AGP
            ['?papa=334&categoria=378', 'VideoCard'],  # VGA PCIe Nvidia
            ['?papa=334&categoria=454', 'VideoCard'],  # VGA PCIe ATI
            ['?papa=334&categoria=455', 'VideoCard'],  # VGA Profesionales
            ['?papa=272&categoria=272', 'Processor'],
            ['?papa=256&categoria=250', 'Monitor'],  # Monitores LCD
            ['?papa=256&categoria=260', 'Television'],  # Televisores LCD
            ['?papa=292&categoria=292', 'Motherboard'],
            ['?papa=264&categoria=112', 'Ram'],  # Memoria PC
            ['?papa=264&categoria=482', 'Ram'],  # Memoria PC High-End
            ['?papa=264&categoria=100', 'Ram'],  # Memoria Notebook
            ['?papa=264&categoria=266', 'Ram'],  # Memoria Server
            ['?papa=312&categoria=340', 'StorageDrive'],  # HDD PC
            ['?papa=312&categoria=421', 'StorageDrive'],  # HDD Notebook
            ['?papa=326&categoria=54', 'PowerSupply'],  # Fuentes de poder
        ]

        product_links = {}
        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue

            url = url_base + '/' + url_extension

            soup = BeautifulSoup(browser.open(url).get_data())

            try:
                page_count = soup.findAll('table',
                        {'class': 'descripcionbold'})
                page_count = page_count[1].findAll('td', {'align': 'center'})
                page_count = int(page_count[-1].find('a').string)
            except Exception:
                page_count = 1

            for page in range(page_count):
                page += 1

                complete_url = url + '&pagina=' + str(page)

                soup = BeautifulSoup(browser.open(complete_url).get_data())

                product_link_tags = soup.findAll('a',
                        {'class': 'vinculoNombreProd'})

                for product_link in product_link_tags:
                    link = url_base + product_link['href']
                    link = link.encode('ascii', 'ignore')
                    if link not in product_links:
                        product_links[link] = ptype

        return product_links.items()
