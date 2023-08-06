from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class Dell(Store):
    @classmethod
    def product_types(cls):
        return [
            'Notebook',
            'Monitor',
        ]

    @classmethod
    def _retrieve_product(cls, url):
        br = mechanize.Browser()
        data = br.open(url).get_data()
        soup = BeautifulSoup(data)

        title = soup.find('div', {'id': 'scpcc_title'}).find('img')['alt']
        title = title.encode('ascii', 'ignore')

        price = soup.find(['tr', 'td'], {'class': 'pricing_dotdotdot'})
        price = price.findAll('span')[-1].string.split('$')[1]
        price = Decimal(clean_price_string(price))

        prices = {}
        for p in ['credit_card', 'deposit', 'wire_transfer']:
            prices[p] = price

        return [title, prices]

    @classmethod
    def _product_urls_and_types(cls, product_types):
        cookies = mechanize.CookieJar()
        opener = mechanize.build_opener(mechanize.HTTPCookieProcessor(cookies))
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (MyProgram/0.1)'),
            ('From', 'responsible.person@example.com')]
        mechanize.install_opener(opener)

        url_buscar_productos = '/cl/'
        product_links = []
        url_base = 'http://www.dell.com'

        # Start home
        if 'Notebook' in product_types:
            url_extensions = [
                'p/laptops?cat=laptops',
            ]

            for url_extension in url_extensions:
                url_webpage = url_base + url_buscar_productos + url_extension

                r = mechanize.urlopen(url_webpage)
                soup = BeautifulSoup(r.read())

                notebook_lines_container = soup.find('div',
                    'tabschegoryGroups')
                notebook_lines = notebook_lines_container.findAll('div',
                    recursive=False)

                notebook_urls = []
                for line in notebook_lines:
                    for container in line.findAll('div', 'prodImg'):
                        link = container.find('a')['href'].replace('pd', 'fs')
                        notebook_urls.append(url_base + link)

                for url in notebook_urls:
                    for url in cls.retrieve_line_links(url):
                        product_links.append([url, 'Notebook'])

            # Start business

            url_extensions = [
                'empresas/p/laptops',
                ]

            for url_extension in url_extensions:
                url_webpage = url_base + url_buscar_productos + url_extension
                r = mechanize.urlopen(url_webpage)
                soup = BeautifulSoup(r.read())

                line_links = soup.find('div', 'content').findAll('a')
                for link in line_links:
                    url = url_base + link['href']
                    for url in cls.retrieve_enteprise_links(url):
                        product_links.append([url, 'Notebook'])

        # Start Monitor

        if 'Monitor' in product_types:
            url_extensions = [
                '/content/products/compare.aspx/19_22widescreen'
                '?c=cl&cs=cldhs1&l=es&s=dhs',
                '/content/products/compare.aspx/23_30widescreen'
                '?c=cl&cs=cldhs1&l=es&s=dhs',
                '/cl/es/empresas/Monitores/19_15widescreen/cp.aspx'
                '?refid=19_15widescreen&s=bsd&cs=clbsdt1',
                '/cl/es/empresas/Monitores/22_20widescreen/cp.aspx'
                '?refid=22_20widescreen&s=bsd&cs=clbsdt1',
                '/cl/es/empresas/Monitores/30_24widescreen/cp.aspx'
                '?refid=30_24widescreen&s=bsd&cs=clbsdt1',
                '/cl/es/empresas/Monitores/20_19flatpanel/cp.aspx'
                '?refid=20_19flatpanel&s=bsd&cs=clbsdt1',
                ]

            for url_extension in url_extensions:
                url_webpage = url_base + url_extension

                r = mechanize.urlopen(url_webpage)
                soup = BeautifulSoup(r.read())

                links = soup.findAll('a', {'class': 'lnk'})
                for link in links:
                    if 'configure' in link['href']:
                        product_links.append([link['href'], 'Monitor'])

        return product_links

    @classmethod
    def retrieve_enteprise_links(cls, url):
        me = mechanize.urlopen(url)
        soup = BeautifulSoup(me.read())

        urls = []
        for link in soup.findAll('a', 'purchase'):
            url = 'http://www.dell.com' + link['href']
            urls.extend(cls.retrieve_line_links(url))

        return urls

    @classmethod
    def retrieve_line_links(cls, url):
        me = mechanize.urlopen(url)
        soup = BeautifulSoup(me.read())
        custom_config_containers = soup.findAll('div', 'buttons')

        real_url = me.geturl()

        if not custom_config_containers and 'configure' in real_url:
            return [real_url]

        links = []
        for container in custom_config_containers:
            links.append(container.find('a')['href'])

        return links
