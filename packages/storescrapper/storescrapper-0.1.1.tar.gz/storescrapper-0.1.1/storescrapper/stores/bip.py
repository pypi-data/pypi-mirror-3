from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class Bip(Store):

    @classmethod
    def extract_links(cls, pageUrl):
        br = mechanize.Browser()
        data = br.open(pageUrl).get_data()
        soup = BeautifulSoup(data)
        links = soup.findAll('a', {'class': 'menuprod'})[::2]

        return links

    @classmethod
    def _retrieve_product(cls, url):
        br = mechanize.Browser()
        data = br.open(url).get_data()
        soup = BeautifulSoup(data)

        stock_info = soup.find('td', {'class': 'disp'})

        if not stock_info:
            return None

        stock_string = ''.join(str(stock) for stock in stock_info.contents)

        if 'Agotado' in stock_string:
            return None

        title_span = soup.find('td', {'class': 'menuprodg'})
        title = title_span.contents[0].strip()

        price_cell = soup.findAll('td', {'class': 'prcm'})
        price = Decimal(clean_price_string(price_cell[0].string))

        name = title.encode('ascii', 'ignore').strip()

        return [name, price]

    @classmethod
    def _product_urls_and_types(cls, product_types):
        url_base = 'http://www.bip.cl/ecommerce/'
        url_buscar_productos = 'index.php?modulo=busca&'

        url_extensions = [
            # Netbooks
            ['categoria=191', 'Notebook'],
            # Notebooks
            ['categoria=166', 'Notebook'],
            # Tarjetas de video
            ['categoria=118&categoria_papa=97', 'VideoCard'],
            # Proces Intel 775
            ['categoria=99&categoria_papa=111', 'Processor'],
            # Proces Intel 1155
            ['categoria=339&categoria_papa=111', 'Processor'],
            # Proces Intel 1156
            ['categoria=262&categoria_papa=111', 'Processor'],
            # Proces Intel 1366
            ['categoria=263&categoria_papa=111', 'Processor'],
            # Proces AMD AM2
            ['categoria=100&categoria_papa=111', 'Processor'],
            # Proces AMD AM3
            ['categoria=242&categoria_papa=111', 'Processor'],
            # LCD
            ['categoria=19', 'Screen'],
            # Placas madre
            ['categoria=108', 'Motherboard'],
            # RAM PC
            ['categoria=132', 'Ram'],
            # RAM Notebook
            ['categoria=178', 'Ram'],
            # RAM Servidor
            ['categoria=179', 'Ram'],
            # Disco Duro 2,5'
            ['categoria=125&categoria_papa=123', 'StorageDrive'],
            # Disco Duro 3,5'
            ['categoria=124&categoria_papa=123', 'StorageDrive'],
            # Fuentes de poder
            ['categoria=88&categoria_papa=114', 'PowerSupply'],
        ]

        product_links = []

        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue

            page_number = 0

            while True:
                url_webpage = url_base + url_buscar_productos + url_extension \
                             + '&pagina=' + str(page_number)

                raw_links = cls.extract_links(url_webpage)
                if not raw_links:
                    break
                for raw_link in raw_links:
                    product_links.append([url_base + raw_link['href'], ptype])

                page_number += 1

        return product_links
