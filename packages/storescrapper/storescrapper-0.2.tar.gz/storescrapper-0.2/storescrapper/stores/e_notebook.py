from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class ENotebook(Store):
    @classmethod
    def product_types(cls):
        return [
            'Notebook',
            'Ram',
            'StorageDrive'
        ]

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()
        product_data = browser.open(url).get_data()
        product_soup = BeautifulSoup(product_data)

        product_cells = product_soup.findAll('td', {'class': 'pageHeading'})

        product_name = product_cells[0].find('h1').contents[0]

        cells = [
            [product_cells[1], ['cash']],
            [product_cells[2], ['deposit', 'debit_card', 'credit_card',
                                'presto_card']],
        ]

        prices = {}
        for cell, payment_methods in cells:
            try:
                product_price = Decimal(clean_price_string(cell.find('span',
                        {'class': 'productSpecialPrice'}).string))
            except Exception:
                product_price = Decimal(clean_price_string(
                    cell.string.split('$')[1]))

            for p in payment_methods:
                prices[p] = product_price

        return [product_name, prices]

    @classmethod
    def _product_urls_and_types(cls, product_types):
        url_base = 'http://www.notebook.cl/'
        url_buscar_productos = 'venta/'

        browser = mechanize.Browser()

        url_extensions = [
            ['it-index-n-notebooks-cP-1.html', 'Notebook'],
        ]

        extra_pagelinks = [
            ['it-index-n-memoria_notebook-cP-46_4.html', 'Ram'],
            ['it-index-n-discos_duros-cP-46_23.html', 'StorageDrive'],
        ]

        page_links = []
        for url_extension, ptype in url_extensions:
            if ptype not in product_types:
                continue
            urlWebpage = url_base + url_buscar_productos + url_extension

            base_soup = BeautifulSoup(browser.open(urlWebpage).get_data())

            table_navigator = base_soup.findAll('table',
                    {'cellpadding': '2'})[1]

            pageNavigator = table_navigator.findAll('td',
                    {'class': 'smallText'})
            for pn in pageNavigator:
                link = pn.find('a')
                try:
                    page_links.append([link['href'].split('?osCsid')[0],
                                       ptype])
                except Exception:
                    continue

        for page_link, ptype in extra_pagelinks:
            if ptype not in product_types:
                continue
            page_links.append([url_base + url_buscar_productos + page_link,
                               ptype])

        product_link_pages = []
        for pageLink, ptype in page_links:
            links = cls.extract_product_pages(pageLink)
            for link in links:
                product_link_pages.append([link, ptype])

        product_links = []
        for product_link_page, ptype in product_link_pages:
            for link in cls.extract_product_links(product_link_page):
                product_links.append([link, ptype])

        return product_links

    @classmethod
    def extract_product_links(cls, page_link):
        br = mechanize.Browser()
        data = br.open(page_link).get_data()
        soup = BeautifulSoup(data)
        product_links = []
        cells = soup.findAll('td', {'class': 'productListing-data'})[1::4]
        for i in range(len(cells)):
            link = cells[i].find('a')
            product_links.append(link['href'].split('?osCsid')[0])
        return product_links

    @classmethod
    def extract_product_pages(cls, base_page_link):
        br = mechanize.Browser()
        data = br.open(base_page_link).get_data()
        soup = BeautifulSoup(data)
        links = [base_page_link]
        pageLinks = soup.findAll('a', {'class': 'pageResults'})[:-1]
        for pageLink in pageLinks:
            link = pageLink['href'].split('&osCsid')[0]
            links.append(link)

        return links
