from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class PcExpress(Store):

    @classmethod
    def _retrieve_product(cls, url):
        br = mechanize.Browser()
        data = br.open(url).get_data()
        soup = BeautifulSoup(data)

        name = soup.findAll('b')[2].string.encode('ascii', 'ignore')

        price = soup.find('font', {'size': '3'}).find('span').find('span')
        price = Decimal(clean_price_string(price.find('b').string))

        return name, price

    @classmethod
    def _product_urls_and_types(cls, product_types):
        browser = mechanize.Browser()

        url_extensions = [
            ['75_136', 'Notebook'],   # Notebooks
            ['83_157', 'VideoCard'],   # Tarjetas de video AGP
            ['83_158', 'VideoCard'],   # Tarjetas de video PCIe AMD
            ['83_159', 'VideoCard'],   # Tarjetas de video PCIe Nvidia
            ['61_85', 'Processor'],    # Procesadores AM2
            ['61_84', 'Processor'],    # Procesadores AM3
            ['61_86', 'Processor'],    # Procesadores 775
            ['61_193', 'Processor'],   # Procesadores 1155
            ['61_87', 'Processor'],    # Procesadores 1156
            ['61_165', 'Processor'],   # Procesadores 1366
            ['73_128', 'Monitor'],   # LCD
            ['73_129', 'Television'],   # LCD/TV
            ['73_171', 'Monitor'],   # LED
            ['60_88', 'Motherboard'],   # Placas madre AM2
            ['60_89', 'Motherboard'],   # Placas madre AM3
            ['60_90', 'Motherboard'],   # Placas madre 775
            ['60_194', 'Motherboard'],   # Placas madre 1155
            ['60_91', 'Motherboard'],   # Placas madre 1156
            ['60_186', 'Motherboard'],   # Placas madre 1366
            ['72_126', 'Ram'],   # RAM Desktop
            ['72_127', 'Ram'],   # RAM Notebook
            ['62_101', 'StorageDrive'],   # HDD PC
            ['62_103', 'StorageDrive'],   # HDD Notebook
            ['70_118', 'PowerSupply'],   # Fuentes de poder
        ]

        product_links = []

        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue
            url = 'http://www.pc-express.cl/index.php?cPath=' + \
                         url_extension

            soup = BeautifulSoup(browser.open(url).get_data())

            td_products = soup.findAll('td',
                    {'class': 'wrapper_pic_br wrapper_pic_td'})

            for td_product in td_products:
                link = td_product.find('a')['href']
                product_links.append([link, ptype])

        return product_links
