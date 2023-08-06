from storescrapper.utils import format_currency


class Product(object):
    """
    Class that abstracts the information of a scrapped product
    """

    def __init__(self, name, price, url, type, store):
        """
        Constructor of the Product class

        :param name: Name of the product
        :type name: unicode
        :param price: Price of the product or None if it is not available
        :type price: object
        :param url: URL of the product in the store website
        :type url: unicode
        :param type: Type of the product
        :type type: unicode
        :param store: Name of the store where the product was found
        :type store: unicode
        """

        self.price = price
        self.name = name
        self.url = url
        self.type = type
        self.store = store

    def __repr__(self):
        return unicode(self)

    def __str__(self):
        return unicode(self)

    def __eq__(self, other):
        attrs = ['price', 'name', 'url', 'type', 'store']

        for attr in attrs:
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __unicode__(self):
        result = u'{0} - {1} ({2})\n{3}\n'.format(self.store, self.name,
            self.type, self.url)
        if self.price is not None:
            result += format_currency(self.price)
        else:
            result += u'Not available'
        return result

    def is_available(self):
        """
        Returns True if the product is available

        :rtype: bool
        """
        return self.price is not None
