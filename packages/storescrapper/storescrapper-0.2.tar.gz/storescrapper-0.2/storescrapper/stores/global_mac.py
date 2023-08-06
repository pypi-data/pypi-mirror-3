from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class GlobalMac(Store):
    @classmethod
    def product_types(cls):
        return [
            'Notebook',
            'Monitor',
            'Ram',
            'StorageDrive'
        ]

    @classmethod
    def _retrieve_product(cls, url):
        cookies = mechanize.CookieJar()
        opener = mechanize.build_opener(mechanize.HTTPCookieProcessor(cookies))
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (MyProgram/0.1)'),
            ('From', 'responsible.person@example.com')]
        mechanize.install_opener(opener)
        browser = mechanize.Browser()
        product_data = browser.open(url).get_data()
        soup = BeautifulSoup(product_data)

        product_name = soup.find('h1').string.encode('ascii', 'ignore')
        product_price = soup.find('span', {'id': 'product_price'})
        product_price = Decimal(clean_price_string(product_price.string))

        payment_methods = ['cash', 'deposit', 'wire_transfer']

        additional_data = soup.find('td', 'descr').findAll('h3')

        if not additional_data:
            payment_methods.extend(['debit_card', 'credit_card'])
        elif 'Contado' not in additional_data[0].string:
            payment_methods.extend(['debit_card', 'credit_card'])

        prices = {}
        for p in payment_methods:
            prices[p] = product_price

        return [product_name, prices]

    @classmethod
    def _product_urls_and_types(cls, product_types):
        cookies = mechanize.CookieJar()
        opener = mechanize.build_opener(mechanize.HTTPCookieProcessor(cookies))
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (MyProgram/0.1)'),
            ('From', 'responsible.person@example.com')]
        mechanize.install_opener(opener)
        url_base = 'http://www.globalmac.cl/'

        browser = mechanize.Browser()

        url_extensions = [
            ['MacBook/', 'Notebook'],
            ['MacBook-Pro/', 'Notebook'],
            ['Monitores-LCD/', 'Monitor'],
            ['Cinema-Display/', 'Monitor'],
            ['Disco-Duro-SATA-2.5/', 'StorageDrive'],
            ['Discos-Duros-SATA/', 'StorageDrive'],
        ]

        if 'Ram' in product_types:
            memory_catalog_url = url_base + 'Memorias/'
            base_data = browser.open(memory_catalog_url).get_data()
            soup = BeautifulSoup(base_data)
            subcats = soup.findAll('span', {'class': 'subcategories'})
            for subcat in subcats:
                link = subcat.find('a')['href'].replace(url_base, '')
                url_extensions.append([link, 'Ram'])

        product_links = []

        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue
            base_data = browser.open(url_base + url_extension).get_data()
            soup = BeautifulSoup(base_data)

            titles = soup.findAll('a', {'class': 'product-title'})

            for title in titles:
                product_links.append([title['href'], ptype])

        return product_links
