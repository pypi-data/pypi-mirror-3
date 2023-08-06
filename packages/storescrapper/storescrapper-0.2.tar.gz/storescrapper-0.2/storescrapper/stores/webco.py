from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class Webco(Store):
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
            'PowerSupply',
            ]

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()
        product_soup = BeautifulSoup(browser.open(url).get_data())

        name = product_soup.find('h1').contents[0].encode('ascii', 'ignore')
        name = name.strip()

        prices = {}

        cash_price = product_soup.findAll('h2')[1].string.replace('cash', '')
        cash_price = Decimal(clean_price_string(cash_price))

        for p in ['cash', 'deposit', 'wire_transfer']:
            prices[p] = cash_price

        normal_price = product_soup.find('h2').find('a').string
        normal_price = Decimal(clean_price_string(normal_price))

        for p in ['check', 'debit_card', 'credit_card', 'ripley_card',
                  'presto_card']:
            prices[p] = normal_price

        return name, prices

    @classmethod
    def _product_urls_and_types(cls, product_types):
        url_base = 'http://www1.webco.cl/'
        browser = mechanize.Browser()

        url_extensions = [
            # Netbooks
            ['n_new_productos.asp?CATEGORIA={761FD739-2D0F-4177-8AE0-'
             'C641D6F16502}', 'Notebook'],
            # Notebooks
            ['n_new_productos.asp?CATEGORIA={D70BBB30-F5E9-4246-B812-'
             'A939C8777429}', 'Notebook'],
            # Tarjetas de video
            ['n_new_productos.asp?CATEGORIA={FFE74755-6E24-4958-A066-'
             'F75670943D3E}', 'VideoCard'],
            # Procesadores AMD
            ['n_new_productos.asp?CATEGORIA={AA5D5535-B127-4AEE-8583-'
             '4529F66DE4D7}#ct_39', 'Processor'],
            # Procesadores Intel
            ['n_new_productos.asp?CATEGORIA={5701C20F-03E6-430E-8CCF-'
             '01EE820BEDF8}#ct_39', 'Processor'],
            # LCD TV
            ['n_new_productos.asp?CATEGORIA={E49A199E-214A-4658-99AA-'
             '7E6220434D8D}#ct_32', 'Television'],
            # LCD
            ['n_new_productos.asp?CATEGORIA={79A1AF72-4B4D-4368-9205-'
             'FC0D646A1145}#ct_32', 'Monitor'],
            # MB AMD
            ['n_new_productos.asp?CATEGORIA={C29A8E9A-5B73-4BEC-B6D7-'
             '665BA1B0D087}#ct_38', 'Motherboard'],
            # MB Intel
            ['n_new_productos.asp?CATEGORIA={9892E74D-67CD-4443-86F7-'
             '6FEBE141596B}#ct_38', 'Motherboard'],
            # HDD Notebook
            ['n_new_productos.asp?CATEGORIA={BCFA52D6-A416-4C48-BA90-'
             'F490B4F2C651}#ct_421', 'StorageDrive'],
            # HDD Notebook
            ['n_new_productos.asp?CATEGORIA={BCFA52D6-A416-4C48-BA90-'
             'F490B4F2C651}#ct_421', 'StorageDrive'],
            # HDD SATA
            ['n_new_productos.asp?CATEGORIA={80024ADB-0B06-4281-8CB6-'
             '7649D9E2C29B}#ct_421', 'StorageDrive'],
            # HDD IDE
            ['n_new_productos.asp?CATEGORIA={518AE532-05F0-4FEB-9FBE-'
             '3E67CA383E91}#ct_421', 'StorageDrive'],
            # RAM Desktop
            ['n_new_productos.asp?CATEGORIA={CB3ACADF-536F-4513-BD91-'
             '41E5E210B742}#ct_31', 'Ram'],
            # RAM Notebook
            ['n_new_productos.asp?CATEGORIA={B77F75B2-F280-4385-892A-'
             '01109D48ABD3}#ct_31', 'Ram'],
            # Fuentes de poder
            ['n_new_productos.asp?CATEGORIA={B54741A6-B995-4AB3-8FC5-'
             'BFB1FB1B5464}#ct_22', 'PowerSupply'],
            ]

        product_links = {}
        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue
            url = url_base + url_extension
            soup = BeautifulSoup(browser.open(url).get_data())

            product_link_tags = soup.findAll('a')

            for link in product_link_tags:
                try:
                    url = url_base + link['href']
                    if url not in product_link_tags:
                        product_links[url] = ptype
                except Exception:
                    continue

        return product_links.items()
