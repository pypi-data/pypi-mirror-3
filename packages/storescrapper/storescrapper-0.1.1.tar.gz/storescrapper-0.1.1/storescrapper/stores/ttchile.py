from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class TtChile(Store):

    @classmethod
    def _retrieve_product(cls, url):
        base_data = mechanize.urlopen(url)
        base_soup = BeautifulSoup(base_data)

        image = base_soup.findAll('div', {'class': 'textOtrosPrecios'})[2]
        image = image.find('img')['src']
        if 'agotado' in image or 'proximo' in image:
            return None

        title = base_soup.find('div', {'class': 'textTituloProducto'})
        title = title.string.strip().encode('ascii', 'ignore')

        prices = base_soup.findAll('div', {'class': 'textPrecioContado'})
        price = prices[0].string
        price = Decimal(clean_price_string(price))

        return [title, price]

    @classmethod
    def _product_urls_and_types(cls, product_types):
        url_base = 'http://www.ttchile.cl/'
        product_urls_and_types = []

        url_extensions = [
            ['subpro.php?ic=21&isc=20', 'Notebook'],    # Notebooks
            ['catpro.php?ic=31', 'VideoCard'],          # Tarjetas de video
            ['catpro.php?ic=25', 'Processor'],          # Procesadores AMD
            ['catpro.php?ic=26', 'Processor'],          # Procesadores Intel
            ['catpro.php?ic=18', 'Screen'],             # LCD
            ['catpro.php?ic=23', 'Motherboard'],        # MB AMD
            ['catpro.php?ic=24', 'Motherboard'],        # MB Intel
            ['subpro.php?ic=16&isc=10', 'Ram'],         # RAM DDR
            ['subpro.php?ic=16&isc=11', 'Ram'],         # RAM DDR2
            ['subpro.php?ic=16&isc=12', 'Ram'],         # RAM DDR3
            ['subpro.php?ic=16&isc=13', 'Ram'],         # RAM Notebook
            ['subpro.php?ic=10&isc=4', 'StorageDrive'],  # HDD IDE
            ['subpro.php?ic=10&isc=6', 'StorageDrive'],  # HDD Notebook
            ['subpro.php?ic=10&isc=5', 'StorageDrive'],  # HDD SATA
            ['subpro.php?ic=10&isc=7', 'StorageDrive'],  # SSD
            ['catpro.php?ic=12', 'PowerSupply'],        # Fuentes de poder
        ]

        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue

            page_number = 1

            while True:
                url = url_base + url_extension + '&pagina=' + \
                              str(page_number)
                base_data = mechanize.urlopen(url)
                base_soup = BeautifulSoup(base_data)

                divs = base_soup.findAll('div', {'class': 'linkTitPro'})
                product_links = [div.find('a')['href'] for div in divs]

                if not product_links:
                    break

                for product_link in product_links:
                    url = url_base + product_link
                    product_urls_and_types.append([url, ptype])

                page_number += 1

        return product_urls_and_types
