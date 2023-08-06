from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class TopPc(Store):

    @classmethod
    def _retrieve_product(cls, url):
        br = mechanize.Browser()
        soup = BeautifulSoup(br.open(url).get_data())

        name = soup.find('h2').string
        price = soup.find('span', {'id': 'our_price_display'}).string
        price = Decimal(clean_price_string(price))

        return name, price

    @classmethod
    def _product_urls_and_types(cls, product_types):
        browser = mechanize.Browser()

        url_extensions = [
            ['76', 'VideoCard'],    # Tarjetas de video
            ['5', 'Processor'],     # Procesadores
            ['61', 'Monitor'],    # Monitores y TV
            ['153', 'Notebook'],   # Notebooks
            ['8', 'Motherboard'],   # MB
            ['11', 'Ram'],   # RAM
            ['17', 'StorageDrive'],   # HDD SATA
            ['34', 'StorageDrive'],   # HDD IDE Desktop
            ['35', 'StorageDrive'],   # HDD IDE Notebook
        ]

        product_links = []

        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue
            url = 'http://www.toppc.cl/beta/category.php?n=50&id_category=' + \
                  url_extension

            soup = BeautifulSoup(browser.open(url).get_data())
            raw_links = soup.findAll('a', {'class': 'product_img_link'})

            for raw_link in raw_links:
                link = raw_link['href']
                product_links.append([link, ptype])

        return product_links
