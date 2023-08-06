from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
import re
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class Falabella(Store):
    force_sync = True

    @classmethod
    def product_types(cls):
        return [
            'Notebook',
            'Television'
        ]

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()

        product_data = browser.open(url).get_data()
        product_soup = BeautifulSoup(product_data)

        pn = product_soup.find('div',
                {'id': 'destacadoRuta'}).find('a').string

        if not pn:
            return None

        pn = pn.replace('&nbsp;', ' ').replace('\r', ' ').replace('\n', ' ')
        pn = ' '.join(re.split('\s+', pn.replace('\t', ' ')))
        product_name = pn.encode('ascii', 'ignore')

        product_price = product_soup.find('div', {'class': 'precio1'})
        product_price = Decimal(clean_price_string(product_price.contents[2]))

        return [product_name, product_price]

    @classmethod
    def _product_urls_and_types(cls, product_types):
        browser = mechanize.Browser()

        url_schemas = [
            ['http://www.falabella.com/falabella-cl/browse/productList.jsp?'
             '_dyncharset=iso-8859-1&requestChainToken=0005653415&pageSize=16&'
             'priceFlag=&categoryId=cat70057&docSort=numprop&docSortProp=price'
             '&docSortOrder=ascending&onlineStoreFilter=online'
             '&userSelectedFormat=4*4&trail=SRCH%3Acat70057&navAction=jump'
             '&searchCategory=true&question=cat70057'
             '&qfh_s_s=submit&_D%3Aqfh_s_s=+'
             '&qfh_ft=SRCH%3Acat70057&_D%3Aqfh_ft=+'
             '&_DARGS=%2Ffalabella-cl%2Fbrowse%2FfacetsFunctions.jsp'
             '&goToPage=', 'Notebook'],
            ['http://www.falabella.com/falabella-cl/browse/productList.jsp?'
             '_dyncharset=iso-8859-1&requestChainToken=0005655243&pageSize=16&'
             'priceFlag=&categoryId=cat70043&docSort=numprop&docSortProp=price'
             '&docSortOrder=ascending&onlineStoreFilter=online'
             '&userSelectedFormat=4*4&trail=SRCH%3Acat70043&navAction=jump'
             '&searchCategory=true&question=cat70043&qfh_s_s=submit'
             '&_D%3Aqfh_s_s=+&qfh_ft=SRCH%3Acat70043&_D%3Aqfh_ft=+'
             '&_DARGS=%2Ffalabella-cl%2Fbrowse%2FfacetsFunctions.jsp'
             '&goToPage=', 'Television'],
            ['http://www.falabella.com/falabella-cl/browse/productList.jsp?'
             '_dyncharset=iso-8859-1&requestChainToken=0005655389&pageSize=16&'
             'priceFlag=&categoryId=cat2053&docSort=numprop&docSortProp=price'
             '&docSortOrder=ascending&onlineStoreFilter=online'
             '&userSelectedFormat=4*4&trail=SRCH%3Acat2053&navAction=jump'
             '&searchCategory=true&question=cat2053&qfh_s_s=submit'
             '&_D%3Aqfh_s_s=+&qfh_ft=SRCH%3Acat2053&_D%3Aqfh_ft=+'
             '&_DARGS=%2Ffalabella-cl%2Fbrowse%2FfacetsFunctions.jsp'
             '&goToPage=', 'Television'],
            ['http://www.falabella.com/falabella-cl/browse/productList.jsp?'
             '_dyncharset=iso-8859-1&requestChainToken=0005655389&pageSize=16&'
             'priceFlag=&categoryId=cat70044&docSort=numprop&docSortProp=price'
             '&docSortOrder=ascending&onlineStoreFilter=online'
             '&userSelectedFormat=4*4&trail=SRCH%3Acat70044&navAction=jump'
             '&searchCategory=true&question=cat70044&qfh_s_s=submit'
             '&_D%3Aqfh_s_s=+&qfh_ft=SRCH%3Acat70044&_D%3Aqfh_ft=+'
             '&_DARGS=%2Ffalabella-cl%2Fbrowse%2FfacetsFunctions.jsp'
             '&goToPage=', 'Television'],

        ]
        product_links = []

        for url_schema, ptype in url_schemas:
            if ptype not in product_types:
                continue
            page_number = 1

            while True:
                url = url_schema + str(page_number)

                baseData = browser.open(url).get_data()
                baseSoup = BeautifulSoup(baseData)

                mosaicDivs = baseSoup.findAll('div', {'class': 'quickView'})

                if not mosaicDivs:
                    break

                for div in mosaicDivs:
                    url = 'http://www.falabella.com' + div.find('a')['href']
                    url = url.replace(' ', '')

                    m = re.search(';jsessionid=\S+\.node\d', url)
                    if m:
                        url = url[:m.start()] + url[m.end():]

                    url = ''.join(url.split())
                    product_links.append([url, ptype])

                page_number += 1

        return product_links
