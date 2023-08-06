import logging
import traceback
from celery.task import task
from celery.task.sets import TaskSet
from storescrapper.exceptions.store_scrap_error import StoreScrapError
from storescrapper.product import Product


class Store(object):
    """
    Common superclass of all the scrap store scripts

    Implements the APIs to conveniently scrap the products of the available
    stores in storecrapper.stores using synchronous methods or
    asynchronous tasks.
    """

    ####################
    # API of the class #
    ####################

    @classmethod
    def products(cls, product_types, async=True):
        """
        Retrieves the available products in the store that match one
        of the given product types.

        Returns a dictionary of unicode => Product matching the URL of the
        product with its complete data. If the product is unavailable the value
        of the pairing is None.

        :param product_types: List of product types
        :type product_types: list of unicode
        :param async: True to use asynchronous tasks
        :type async: bool

        :rtype: dict of storescrapper.product.Product

        """

        # If the store can't handle concurrent connections, force sync
        if hasattr(cls, 'force_sync') and getattr(cls, 'force_sync'):
            async = False

        logging.info('Retrieving products from {0} with types {1}'.format(
            cls.__name__, product_types))

        # Retrieve the URLs of the products
        product_urls_and_types = cls.product_urls_and_types(product_types,
            async=async)
        products = {}

        if async:
            logging.info('Using asynchronous tasks')
            # Dispatch a task for each of the URLs retrieved previously
            tasks = []
            func = cls.retrieve_product
            for url, product_type in product_urls_and_types:
                logging.info('Dispatching task for product with URL {0} ' \
                             'and type {1}'.format(url, product_type))
                tasks.append(func.subtask((cls, url, product_type)))

            job = TaskSet(tasks)
            job_result = job.apply_async()

            logging.info('Waiting for tasks to finish')

            for idx, product in enumerate(job_result.join()):
                logging.info('Result for product with URL: {0}'.format(
                    product_urls_and_types[idx][0]))
                if product:
                    logging.info(product)
                else:
                    logging.info('Not available')

                products[product_urls_and_types[idx][0]] = product

        else:
            logging.info('Using sync method')

            # Get the products one by one
            logging.info('Obtaining products information')
            for url, product_type in product_urls_and_types:
                product = cls.retrieve_product(url, product_type)

                if product:
                    logging.info(product)
                else:
                    logging.info('Not available')

                products[url] = product

        logging.info('Finished fetching products')
        return products

    @classmethod
    def product_urls_and_types(cls, product_types, async=True):
        """
        Returns a list of tuples of the form (url, product_type)
        corresponding to the basic data of the products of the store that
        match the given product types.

        :param product_types: List of product types
        :type product_types: list of unicode
        :param async: True to use asynchronous tasks
        :type async: bool

        :rtype: list of (unicode, unicode)

        """

        # If the store can't handle concurrent connections, force sync
        if hasattr(cls, 'force_sync') and getattr(cls, 'force_sync'):
            async = False

        logging.info('Retrieving product URLs from {0} with types {1}' \
                     ''.format(cls.__name__, product_types))
        if async:
            logging.info('Using async tasks')
            # We optimize the process by creating a task for each product type
            # and dispatching them, as the vast majority of the store classes
            # are faster when dealing with only one product type.
            tasks = []
            func = cls._async_product_urls_and_types
            for product_type in product_types:
                logging.info('Creating task for product type ' \
                             '{0}'.format(product_type))
                tasks.append(func.subtask((cls, product_type)))

            job = TaskSet(tasks)
            job_result = job.apply_async()

            results = []

            logging.info('Waiting for tasks to finish')
            for job_subresult in job_result.join():
                for result in job_subresult:
                    logging.info('Found product URL: {0}'.format(
                        result[0]))
                results.extend(job_subresult)

            logging.info('Finished getting product URLs from ' \
                         '{0}'.format(cls.__name__))

            return results

        else:
            # If the method is called without the async flag we just call the
            # underlying implementation and return the required result.
            logging.info('Using sync method')

            results = [(url, product_type)
                for url, product_type
                in cls.__product_urls_and_types(product_types)]

            for result in results:
                logging.info('Found product URL: {0}'.format(result[0]))

            logging.info('Finished getting product URLs')
            return results

    @classmethod
    @task
    def retrieve_product(cls, url, product_type):
        """
        Obtains the Product corresponding to the given URL or None if it is not
        available.

        :param url: URL of the product in the store
        :type url: unicode
        :param product_type: Product type
        :type product_type: unicode

        :rtype: Product

        """

        logging.info('Retrieving product from {0} with URL {1}'.format(
            cls.__name__, url))

        # Get the product with the underlying implementation
        try:
            product_info = cls._retrieve_product(url)
        except NotImplementedError:
            raise
        except Exception, e:
            message = 'Fetching of product with URL {0} raised '\
                      'exception: {1}'.format(url, e.message)
            logging.error(message)
            formatted_lines = traceback.format_exc().splitlines()
            logging.error(formatted_lines)
            raise StoreScrapError(message)

        # If it is available, load the metadata
        if product_info:
            p = Product(product_info[0], product_info[1], url,
                product_type, unicode(cls.__name__))

            logging.info('Product is available:\n{0}'.format(p))
            return p
        else:
            logging.info('Product is not available')
            return None

    #################################
    # Internal methods of the class #
    #################################

    @classmethod
    @task
    def _async_product_urls_and_types(cls, product_type):
        """
        Retrieves a list of tuples of the form (url, product_type)
        corresponding to the basic data of the products of the store that
        match the given product type.

        In particular this method includes the products that are not
        available in the store but still listed in their webpage.

        :param product_type: Product type
        :type product_type: unicode

        :rtype: list of (unicode, unicode)

        """

        logging.info('Retrieving product URLs from {0} with type {1}'.format(
            cls.__name__, product_type))

        product_urls_and_types = []

        for url, ptype in cls.__product_urls_and_types([product_type]):
            logging.info('Found product URL: {0}'.format(url))
            data = (url, ptype)
            product_urls_and_types.append(data)

        logging.info('Finished getting product URL from {0} with type ' \
                    '{1}'.format(cls.__name__, product_type))

        return product_urls_and_types

    @classmethod
    def __product_urls_and_types(cls, product_types):
        """
        Thin wrapper over the _product_urls_and_types method implemented
        for each store. It only checks for errors and wraps them with some
        metadata and a common exception interface.

        :param product_types: Product types
        :type product_types: list of unicode

        :rtype: list of (unicode, unicode)

        """
        try:
            return cls._product_urls_and_types(product_types)
        except NotImplementedError:
            raise
        except Exception, e:
            message = 'Error while fetching the products from '\
                      '{0} with types {1}: {2}'.format(cls.__name__,
                         product_types, e.message)
            logging.error(message)
            formatted_lines = traceback.format_exc().splitlines()
            logging.error(formatted_lines)
            raise StoreScrapError(message)

    #####################################################################
    # The following methods must be provided by the subclasses of Store #
    #####################################################################

    @classmethod
    def _product_urls_and_types(cls, product_types):
        """
        Returns a list of tuples, each corresponding to the basic information
        (URL and type) of each of the products in the store that match one
        of the given product types.

        :param product_types: List of product types
        :type product_types: list of unicode

        :rtype: list of (unicode, unicode)

        """

        raise NotImplementedError('The subclass of Store should implement '
                                  '_product_urls_and_types and Store should '
                                  'not be instantiated directly')

    @classmethod
    def _retrieve_product(cls, url):
        """
        Returns a list [name, price] corresponding to the name and price of
        the product with the given URL or None if it is not available.

        :param url: URL of the product in the store webpage
        :type url: unicode

        :rtype: (unicode, decimal.Decimal)

        """

        raise NotImplementedError('The subclass of Store should implement '
                                  '_retrieve_product and Store should not be '
                                  'instantiated directly')
