from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store


class Sistemax(Store):
    force_sync = True

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

        name = soup.findAll('h2')[3].find('font').string
        name = name.encode('ascii', 'ignore')

        prices = {}

        cash_price = Decimal(soup.findAll('span', 'style18')[0].string)

        for p in ['cash', 'deposit', 'wire_transfer', 'check']:
            prices[p] = cash_price

        normal_price = Decimal(soup.findAll('span', 'style18')[1].string)

        for p in ['debit_card', 'credit_card', 'presto_card']:
            prices[p] = normal_price

        return name, prices

    @classmethod
    def _product_urls_and_types(cls, product_types):
        base_url = 'http://www.sistemax.cl/webstore/'

        extensions = [
            ['112', 'Notebook'],     # Netbooks
            ['27', 'Notebook'],      # Notebooks
            ['35', 'VideoCard'],     # Tarjetas de video
            ['58', 'Processor'],     # Procesadores AMD
            ['59', 'Processor'],     # Procesadores Intel
            ['25', 'Monitor'],       # Monitores
            ['125', 'Television'],   # Televisores
            ['82', 'Notebook'],      # Mac / iPod
            ['30', 'Motherboard'],   # MB AMD
            ['69', 'Motherboard'],   # MB Intel
            ['24', 'Ram'],           # RAM
            ['16', 'StorageDrive'],  # Discos duros y SSD
            ['21', 'PowerSupply'],   # Fuentes de poder
        ]

        product_links = []
        for extension, ptype in extensions:
            if ptype not in product_types:
                continue
            url = base_url + 'index.php?op=seccion/id=' + extension + \
                  '&page=-1&listar=true'

            browser = mechanize.Browser()

            soup = BeautifulSoup(browser.open(url).get_data())
            info_cells = soup.findAll('td', {'scope': 'col'})

            url_cells = info_cells[3::5]
            urls = [base_url + url_cell.contents[2]['href']
                    for url_cell in url_cells]
            for url in urls:
                product_links.append([url, ptype])

        return product_links
