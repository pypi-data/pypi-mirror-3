from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class PcOfertas(Store):
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
        soup = BeautifulSoup(browser.open(url).get_data())

        name = soup.find('h4', {'class': 'Estilo5'}).string
        name = name.encode('ascii', 'ignore')

        prices = {}

        cash_price = soup.find('span',
                {'style': 'color: #F00; font-size:12px;'})
        cash_price = cash_price.parent.parent.parent.findAll('td')[1].find(
            'span')
        cash_price = int(clean_price_string(cash_price.string))

        for p in ['cash', 'wire_transfer', 'deposit']:
            prices[p] = Decimal(cash_price)

        normal_price = int(round(cash_price / 0.94))

        for p in ['debit_card', 'credit_card', 'presto_card']:
            prices[p] = Decimal(int(round(normal_price * 0.975)))

        for p in ['check']:
            prices[p] = Decimal(int(round(normal_price * 0.98)))

        for p in ['dated_check']:
            prices[p] = Decimal(normal_price)

        return name, prices

    @classmethod
    def _product_urls_and_types(cls, product_types):
        product_links = []

        url_extensions = [
            ['74', 'Notebook'],   # Notebook
            ['75', 'Notebook'],   # Netbook
            ['87', 'VideoCard'],   # Tarjetas de video
            ['18', 'Processor'],   # Procesadores
            ['28', 'Monitor'],   # Monitores
            ['108', 'Motherboard'],   # Placas madre
            ['17', 'Ram'],   # RAM
            ['20', 'StorageDrive'],   # Almacenamiento
            ['72', 'PowerSupply'],   # Fuentes de poder
        ]

        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue
            url = 'http://www.pcofertas.cl/index.php?route=product/' \
                  'category&path=' + url_extension
            links = cls.recursive_retrieve_product_links(url)

            links = list(set(links))

            for link in links:
                base_link, args = link.split('?')
                args = dict([elem.split('=') for elem in args.split('&')])
                del args['path']
                args = ['%s=%s' % (k, v) for k, v in args.items()]
                link = base_link + '?' + '&'.join(args)
                if link not in product_links:
                    product_links.append([link, ptype])

        return product_links

    @classmethod
    def recursive_retrieve_product_links(cls, url):
        browser = mechanize.Browser()
        soup = BeautifulSoup(browser.open(url).get_data())
        prod_links = []

        products_table = soup.findAll('table', {'class': 'list'})
        if not products_table:
            return []
        elif len(products_table) == 2:
            # First get the products on the page
            products_anchor_tags = products_table[1].findAll('a')[::3]
            for anchor_tag in products_anchor_tags:
                link = anchor_tag['href']
                prod_links.append(link)

            # Then the ones on sub categories
            category_links = products_table[0].findAll('a')[::2]
            for anchor_tag in category_links:
                link = anchor_tag['href']
                prod_links.extend(cls.recursive_retrieve_product_links(link))
        else:
            # Page may have only products or only category links
            products_anchor_tags = products_table[0].findAll('a')[::3]
            for anchor_tag in products_anchor_tags:
                link = anchor_tag['href']
                if 'product_id' in link:
                    prod_links.append(link)
                else:
                    prod_links.extend(cls.recursive_retrieve_product_links(
                        link))
        return prod_links
