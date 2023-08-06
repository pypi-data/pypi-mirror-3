from decimal import Decimal
from urllib2 import HTTPError
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


def unescape(s):
    s = s.replace('&lt;', '<')
    s = s.replace('&gt;', '>')
    s = s.replace('&quot;', '"')
    s = s.replace('&apos;', "'")
    s = s.replace('&amp;', '&')
    return s


class AbcDin(Store):

    @classmethod
    def _retrieve_product(cls, url):
        product_details_url = url.split('#')[1]
        try:
            product_webpage = mechanize.urlopen(product_details_url)
        except HTTPError:
            return None
        product_soup = BeautifulSoup(product_webpage.read())

        av_span = product_soup.find('div', {'id': 'caja-compra'}).find('span')
        if av_span:
            return None

        product_name = product_soup.find('td', {'id': 'mainDescr'})
        product_name = product_name.find('h2').contents[0]
        product_name = product_name.encode('ascii', 'ignore')

        try:
            product_price = product_soup.find('div', {'id': 'precioProducto'})
            product_price = product_price.find('strong').string
            product_price = product_price.split('Precio Tarjetas ABCDIN $')[1]
            product_price = Decimal(clean_price_string(product_price))
        except Exception:
            product_price = None

        if not product_price:
            try:
                price = product_soup.find('div', {'id': 'precioProducto'})
                price = price.find('strong').string
                price = price.replace('Precio Internet: $', '')
                product_price = Decimal(clean_price_string(price))
            except Exception:
                product_price = None

        if not product_price:
            price = product_soup.find('div', {'id': 'precioNormal'})
            price = price.find('span').string
            product_price = Decimal(clean_price_string(price))

        return [product_name, product_price]

    @classmethod
    def _product_urls_and_types(cls, product_types):
        cookies = mechanize.CookieJar()
        opener = mechanize.build_opener(mechanize.HTTPCookieProcessor(cookies))
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (compatible)'),
            ('From', 'responsible.person@example.com')]
        mechanize.install_opener(opener)

        xml_resources = [
            ['notebooks', 'Notebook'],
            ['netbooks', 'Notebook'],
            ['LCD', 'Screen'],
        ]

        product_links = []

        for xml_resource, ptype in xml_resources:
            if ptype not in product_types:
                continue
            # Obtain and parse HTML information of the base webpage
            base_url = 'https://www.abcdin.cl/abcdin/catabcdin.nsf/' \
                       '%28webProductosxAZ%29?readviewentries&' \
                       'restricttocategory='
            base_data = mechanize.urlopen(base_url + xml_resource)
            base_soup = BeautifulSoup(base_data.read())

            # Obtain the links to the other pages of the catalog (2, 3, ...)
            ntbks_data = base_soup.findAll('text')

            for ntbk_data in ntbks_data:
                ntbk_data = unescape(ntbk_data.contents[0])
                temp_soup = BeautifulSoup(ntbk_data)
                div = temp_soup.find('div')
                link = 'https://www.abcdin.cl/abcdin/abcdin.nsf#' \
                       'https://www.abcdin.cl' + div.find('a')['href']
                product_links.append([link, ptype])

        return product_links
