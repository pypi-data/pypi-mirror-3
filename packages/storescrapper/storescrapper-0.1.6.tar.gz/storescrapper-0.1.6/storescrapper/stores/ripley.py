from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class Ripley(Store):

    @classmethod
    def _retrieve_product(cls, url):
        browser = mechanize.Browser()
        soup = BeautifulSoup(browser.open(url).get_data())

        name = soup.find('span', {'class': 'textogrisbold'})
        name = name.string.encode('ascii', 'ignore')

        prices = []

        try:
            price = soup.find('span', {'class': 'normalHOME'}).string
            price = Decimal(clean_price_string(price))
            prices.append(price)
        except Exception:
            pass

        try:
            price = soup.find('div', {'class': 'textodetallesrojo'})
            price = price.find('div').string.split('$')[1]
            price = Decimal(clean_price_string(price))
            prices.append(price)
        except Exception:
            pass

        try:
            price = soup.find('div', {'class': 'textodetallesrojo'}).string
            price = price.split('$')[1]
            price = Decimal(clean_price_string(price))
            prices.append(price)
        except Exception:
            pass

        if not prices:
            raise Exception

        price = min(prices)

        return name, price

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
