from decimal import Decimal
from BeautifulSoup import BeautifulSoup
import mechanize
from storescrapper.store import Store
from storescrapper.utils import clean_price_string


class Dell(Store):

    @classmethod
    def _retrieve_product(cls, url):
        br = mechanize.Browser()
        data = br.open(url).get_data()
        soup = BeautifulSoup(data)

        try:
            title = soup.find('div', {'id': 'scpcc_title'}).find('img')['alt']
            title = title.encode('ascii', 'ignore')
        except Exception:
            return None

        price = soup.find(['tr', 'td'], {'class': 'pricing_dotdotdot'})
        price = price.findAll('span')[-1].string.split('$')[1]
        price = Decimal(clean_price_string(price))

        return [title, price]

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
                'p/laptops?avt=series&avtsub=inspiron-mini-netbooks&~ck='
                'supertab-inspiron-mini-netbooks',
            ]

            for url_extension in url_extensions:
                url_webpage = url_base + url_buscar_productos + url_extension

                r = mechanize.urlopen(url_webpage)
                base_soup = BeautifulSoup(r.read())

                tab_navigator = base_soup.find('div',
                        {'class': 'superTabarellaTabContainer'})
                line_urls = [url_base + link['href']
                             for link in tab_navigator.findAll('a')]

                for url in line_urls:
                    product_links.extend(cls.retrieve_line_links(url))

            # Start business

            url_extensions = [
                'empresas/p/laptops.aspx',
                ]

            for url_extension in url_extensions:
                url_webpage = url_base + url_buscar_productos + url_extension
                r = mechanize.urlopen(url_webpage)
                base_soup = BeautifulSoup(r.read())

                line_title_containers = base_soup.findAll('div',
                        {'class': 'productTitle'})
                line_urls = [url_base + div.find('a')['href']
                             for div in line_title_containers if div.find('a')]
                for url in line_urls:
                    product_links.extend(cls.retrieve_line_links(url))

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
                base_soup = BeautifulSoup(r.read())

                links = base_soup.findAll('a', {'class': 'lnk'})
                for link in links:
                    if 'configure' in link['href']:
                        product_links.append([link['href'], 'Monitor'])

        return product_links

    @classmethod
    def retrieve_subline_links(cls, url):
        mecha = mechanize.urlopen(url)
        soup = BeautifulSoup(mecha.read())

        buttons = soup.findAll('div', {'class': 'buttons'})
        links = [button.find('a')['href'] for button in buttons]

        if not links:
            redirected_url = mecha.geturl()
            if 'configure' in redirected_url:
                final_links = [[redirected_url, 'Notebook']]
            else:
                final_links = []
        else:
            final_links = [[link, 'Notebook']
                for link in links if 'configure' in link]

        return final_links

    @classmethod
    def retrieve_line_links(cls, url):
        r = mechanize.urlopen(url)
        soup = BeautifulSoup(r.read())

        sub_line_containers = soup.findAll('div', {'class': 'infoCol'})
        sub_line_urls = [container.find('a')['href']
                         for container in sub_line_containers]
        fixed_urls = ['http://www.dell.com' + url[:-2] + 'fs'
                      for url in sub_line_urls]

        links = []
        for url in fixed_urls:
            links.extend(cls.retrieve_subline_links(url))

        return links
