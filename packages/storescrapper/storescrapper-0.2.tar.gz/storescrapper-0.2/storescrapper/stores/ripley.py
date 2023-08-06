from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class Ripley(Store):
    @classmethod
    def product_types(cls):
        return [
            'Notebook',
            'Television',
        ]

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()
        soup = BeautifulSoup(browser.open(url).get_data())

        name = soup.find('span', {'class': 'textogrisbold'})
        name = name.string.encode('ascii', 'ignore')

        prices = {}

        inet_price = soup.find('div', 'textodetallesrojo')
        if inet_price.string:
            inet_price = inet_price.string
        else:
            inet_price = inet_price.find('div').string

        inet_price = Decimal(clean_price_string(inet_price.split('$')[1]))

        normal_price = soup.find('span', 'normalHOME')
        if normal_price:
            normal_price = Decimal(clean_price_string(
                normal_price.string.split('$')[1]))

        ripley_card_exclusive = soup.find('img', {'src':
                              '/wcsstore/Ripley/en_US/images/tarjeta.gif'})

        if ripley_card_exclusive:
            prices['ripley_card'] = inet_price

            if normal_price:
                for p in ['cash', 'debit_card', 'credit_card']:
                    prices[p] = normal_price
        else:
            for p in ['debit_card', 'credit_card', 'ripley_card']:
                prices[p] = inet_price

            if normal_price:
                prices['cash'] = normal_price

        return name, prices

    @classmethod
    def _product_urls_and_types(cls, product_types):
        url_base = 'http://www.ripley.cl/webapp/wcs/stores/servlet/'

        category_urls = [
            ['categoria-TVRipley-10051-001772-130000-ESP-N--', 'Notebook'],
            ['categoria-TVRipley-10051-001860-130000-ESP-N--', 'Notebook'],
            ['categoria-TVRipley-10051-013040-230000-ESP-N', 'Television'],
        ]

        browser = mechanize.Browser()

        product_links = {}

        for category_url, ptype in category_urls:
            if ptype not in product_types:
                continue
            j = 1
            while True:
                url = url_base + category_url + '?curPg=' + str(j)

                soup = BeautifulSoup(browser.open(url).get_data())

                p_paragraphs = soup.findAll('td', {'class': 'grisCatalogo'})
                p_paragraphs = p_paragraphs[1::3]
                p_paragraphs = [pp.parent.parent for pp in p_paragraphs]

                for p in p_paragraphs:
                    url = url_base + p.find('a')['href']
                    url = url.encode('ascii', 'ignore')
                    if url not in product_links:
                        product_links[url] = ptype

                next_page_link = soup.findAll('a',
                        {'class': 'linknormal4'})[-1]
                if next_page_link.string.strip() != '&gt;&gt;':
                    break

                j += 1

        return product_links.items()
