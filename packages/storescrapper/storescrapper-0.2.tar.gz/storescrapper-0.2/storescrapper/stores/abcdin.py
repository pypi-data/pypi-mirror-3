from decimal import Decimal
from urllib2 import HTTPError
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class AbcDin(Store):
    @classmethod
    def product_types(cls):
        return [
            'Notebook',
            'Television'
        ]

    @classmethod
    def _retrieve_product(cls, url):
        print url
        try:
            product_webpage = mechanize.urlopen(url)
        except HTTPError:
            return [url, {}]

        product_soup = BeautifulSoup(product_webpage.read())

        product_name = product_soup.find('h1', {'id': 'catalog_link'}).string
        product_name = product_name.strip().encode('ascii', 'ignore')

        # Product not available check
        if product_soup.find('span', 'button_bottom'):
            return product_name, {}

        prices = {}

        product_price = product_soup.find('span', {'id': 'offerPrice'}).string
        product_price = Decimal(clean_price_string(product_price))
        for p in ['cash', 'debit_card', 'credit_card', 'abcdin_card']:
            prices[p] = product_price

        return [product_name, prices]

    @classmethod
    def _product_urls_and_types(cls, product_types):
        ajax_resources = [
            ['11620', 'Notebook'],
            ['11619', 'Notebook'],
            ['11607', 'Television'],
        ]

        product_links = []

        for category_id, ptype in ajax_resources:
            if ptype not in product_types:
                continue

            url = 'http://www.abcdin.cl/webapp/wcs/stores/servlet/' \
                       'AjaxCatalogSearchResultView?searchTermScope=&' \
                       'searchType=1000&filterTerm=&orderBy=&maxPrice=&' \
                       'showResultsPage=true&langId=-5&beginIndex=0&' \
                       'sType=SimpleSearch&metaData=&pageSize=1000&' \
                       'manufacturer=&resultCatEntryType=&catalogId=' \
                       '10001&pageView=image&searchTerm=&minPrice=&' \
                       'categoryId={0}&storeId=10001'.format(category_id)
            base_data = mechanize.urlopen(url)
            base_soup = BeautifulSoup(base_data.read())

            for ntbk_data in base_soup.findAll('td', 'item'):
                url = ntbk_data.find('a')['href']
                product_links.append([url, ptype])

        return product_links
