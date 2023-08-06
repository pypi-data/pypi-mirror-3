"""
Module that contains only the ProductType class
"""


class ProductType(object):
    """
    Class that abstracts the known product types
    """

    all = [
        'Notebook',
        'Cell',
        'Screen',
        'VideoCard',
        'Processor',
        'Motherboard',
        'Ram',
        'StorageDrive'
    ]

    @staticmethod
    def is_valid_type(product_type):
        """
        Returns True if the given product type is in the list of oficially
        registered types.
        """
        return product_type in ProductType.all
