from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class Rigam(Store):
    @classmethod
    def product_types(cls):
        return [
            'Notebook',
            'VideoCard',
            'Processor',
            'Monitor',
            'Motherboard',
            'Ram',
            'StorageDrive',
            'PowerSupply'
        ]

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()
        product_soup = BeautifulSoup(browser.open(url).get_data())

        name = product_soup.find('td', {'class': 'cy2'}).find('strong')
        name = name.contents[0].encode('ascii', 'ignore')

        availability = product_soup.find('b', {'style': 'color:red;'})
        if availability:
            if 'PRODUCTO AGOTADO' in availability.string:
                return name, {}

        prices = {}

        cash_price = product_soup.find('span', 'cy3').string
        cash_price = Decimal(clean_price_string(cash_price))

        for p in ['cash', 'deposit', 'wire_transfer', 'check']:
            prices[p] = cash_price

        normal_price = product_soup.find('span', 'txtOldPrice').string
        normal_price = Decimal(clean_price_string(normal_price))

        for p in ['credit_card']:
            prices[p] = normal_price

        debit_price = product_soup.findAll('span', 'cy1')[1].string
        debit_price = Decimal(clean_price_string(debit_price))

        for p in ['debit_card']:
            prices[p] = debit_price

        return name, prices

    @classmethod
    def _product_urls_and_types(cls, product_types):
        url_base = 'http://www.rigam.cl/catalogo/'
        browser = mechanize.Browser()

        url_extensions = [
            ['index.php?act=viewCat&catId=39', 'Notebook'],
            ['index.php?act=viewCat&catId=60', 'VideoCard'],
            ['index.php?act=viewCat&catId=40', 'Processor'],
            ['index.php?act=viewCat&catId=2', 'Processor'],
            ['index.php?act=viewCat&catId=54', 'Monitor'],
            ['index.php?act=viewCat&catId=3', 'Motherboard'],
            ['index.php?act=viewCat&catId=52', 'Motherboard'],
            ['index.php?act=viewCat&catId=35', 'Ram'],
            ['index.php?act=viewCat&catId=70', 'StorageDrive'],
            ['index.php?act=viewCat&catId=58', 'StorageDrive'],
            ['index.php?act=viewCat&catId=59', 'PowerSupply'],
        ]

        product_links = []
        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue
            page_number = 0

            while True:
                url = url_base + url_extension + '&page=' + \
                      str(page_number)

                baseSoup = BeautifulSoup(browser.open(url).get_data())

                products_table = baseSoup.find('table', {'class': 'tblList'})

                if not products_table:
                    break

                product_rows = products_table.findAll('tr')[1:]

                for product_row in product_rows:
                    link = product_row.find('a', {'class': 'txtDefault'})
                    product_links.append([url_base + link['href'], ptype])

                page_number += 1

        return product_links
