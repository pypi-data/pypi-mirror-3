import logging
import traceback
from celery.task import task
from celery.task.sets import TaskSet
import mechanize
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
    def products(cls, product_types=list(), async=True):
        """
        Retrieves the products in the store that match one of the given product
        types, if given an empty list this method returns all of the products.

        Returns a list of products. If the product is unavailable its price
        will be None.

        :param product_types: List of product types
        :type product_types: list of unicode
        :param async: True to use asynchronous tasks
        :type async: bool

        :rtype: list of storescrapper.product.Product

        """

        # If the store can't handle concurrent connections, force sync
        if hasattr(cls, 'force_sync') and getattr(cls, 'force_sync'):
            async = False

        if product_types:
            # If product types were given, validate them against the ones the
            # scrapper can handle. This prevents unnecesary work.
            product_types = [ptype for ptype in cls.product_types()
                             if ptype in product_types]
        else:
            # If product types not given, ask the script which ones does it
            # handle. In other words: scrap all the products.
            product_types = cls.product_types()

        logging.info('Retrieving products from {0} with types {1}'.format(
            cls.__name__, product_types))

        # Retrieve the URLs of the products
        product_urls_and_types = cls.product_urls_and_types(product_types,
            async=async)

        products = list()

        if async:
            logging.info('Using asynchronous tasks')
            # Dispatch a task for each of the URLs retrieved previously
            tasks = []
            for url, product_type in product_urls_and_types:
                logging.info('Dispatching task for product with URL {0} ' \
                             'and type {1}'.format(url, product_type))
                tasks.append(cls.retrieve_product.subtask(
                    (cls, url, product_type, False)))

            job_result = TaskSet(tasks).apply_async()

            logging.info('Waiting for tasks to finish')
            try:
                results = job_result.join()
                for idx, product in enumerate(results):
                    logging.info('Result for product with URL: {0}'.format(
                        product_urls_and_types[idx][0]))
                    logging.info(product)
                    products.append(product)
            except StoreScrapError, e:
                # Trigered on the first (and only on the first) scrapping error
                logging.error(e.message)

                # For some reason the logging above does not work if raising
                # the error directly, so a mid variable is needed.
                er = StoreScrapError(e.message)
                raise er

        else:
            logging.info('Using sync method')

            # Get the products one by one, if the scrapping of one of them
            # fails the exception naturally bubbles to the caller.
            logging.info('Obtaining products information')
            for url, product_type in product_urls_and_types:
                product = cls.retrieve_product(url, product_type)
                products.append(product)

        logging.info('Finished scrapping products')
        return products

    @classmethod
    def product_urls_and_types(cls, product_types=list(), async=True):
        """
        Returns a list of tuples of the form (url, product_type)
        corresponding to the basic data of the products of the store that
        match the given product types or all of them if given an empty list.

        :param product_types: List of product types
        :type product_types: list of unicode
        :param async: True to use asynchronous tasks
        :type async: bool

        :rtype: list of (unicode, unicode)

        """

        # If the store can't handle concurrent connections, force sync
        if hasattr(cls, 'force_sync') and getattr(cls, 'force_sync'):
            async = False

        if product_types:
            # If product types were given, validate them against the ones the
            # scrapper can handle. This prevents unnecesary work.
            product_types = [ptype for ptype in cls.product_types()
                             if ptype in product_types]
        else:
            # If product types not given, ask the script which ones does it
            # handle. In other words: scrap all the products.
            product_types = cls.product_types()

        logging.info('Retrieving product URLs from {0} with types {1}' \
                     ''.format(cls.__name__, product_types))
        if async:
            logging.info('Using async tasks')
            # We optimize the process by creating a task for each product type
            # and dispatching them, as the vast majority of the store classes
            # are faster when dealing with only one product type.
            tasks = []
            for product_type in product_types:
                logging.info('Creating task for product type ' \
                             '{0}'.format(product_type))
                tasks.append(cls._async_product_urls_and_types.subtask(
                    (cls, product_type)))

            job_result = TaskSet(tasks).apply_async()
            results = []

            logging.info('Waiting for tasks to finish')
            try:
                for job_subresult in job_result.join():
                    for result in job_subresult:
                        logging.info('Found product URL: {0}'.format(
                            result[0]))
                    results.extend(job_subresult)

                logging.info('Finished getting product URLs from {0}'.format(
                    cls.__name__))

                return results
            except StoreScrapError, e:
                # Triggered on the first scrapping error only, but we send
                # a message including all the product types because the cause
                # is most likely widespread.
                message = 'Error while scrapping the product URLs from '\
                          '{0} with types {1}: {2}'.format(cls.__name__,
                    product_types, e.message)
                logging.error(message)

                # For some reason the logging does not work if raising the
                # error directly, so a mid variable is needed.
                er = StoreScrapError(message)
                raise er

        else:
            # If the method is called without the async flag we just call the
            # underlying implementation and return the required result.
            logging.info('Using sync method')

            try:
                product_urls_and_types = cls._product_urls_and_types_wrapper(
                    product_types)

                results = [(url, product_type)
                    for url, product_type in product_urls_and_types]

                for result in results:
                    logging.info('Found product URL: {0}'.format(result[0]))

                logging.info('Finished getting product URLs')
                return results
            except StoreScrapError, e:
                # Triggered on each scrapping error, but in practice only
                # called once because it raises a second exception.
                message = 'Error while scrapping the product URLs from '\
                          '{0} with types {1}: {2}'.format(cls.__name__,
                    product_types, e.message)
                logging.error(message)
                raise

    @classmethod
    @task
    def retrieve_product(cls, url, product_type, should_log=True):
        """
        Obtains the Product corresponding to the given URL. If the product
        is unavailable its price will be None.

        The product type must be supplied as it is inefficient to deduce it
        from the URL and the store alone. If the type will not be used
        afterwards then it is safe to pass a dummy string for this parameter.

        :param url: URL of the product in the store
        :type url: unicode
        :param product_type: Type of the product that will be retrieved
        :type product_type: unicode
        :param should_log: True if this function should log StoreScrapErrors
        :type should_log: bool

        :rtype: Product
        """

        logging.info('Retrieving product from {0} with URL {1}'.format(
            cls.__name__, url))

        # Get the product with the underlying implementation
        try:
            product_info = cls._retrieve_product(url)
        except (mechanize.HTTPError, mechanize.URLError):
            # Try again!
            product_info = cls._retrieve_product(url)
        except NotImplementedError:
            # Triggered when _retrive_product method is not supplied by the
            # inherited class.
            raise
        except Exception:
            error_message = 'Error scrapping URL from {0}: {1} - {2}'.format(
                cls.__name__,
                url,
                traceback.format_exc().splitlines())
            if should_log:
                logging.error(error_message)
            raise StoreScrapError(error_message)

        # load the metadata
        p = Product(product_info[0], product_info[1], url,
            product_type, unicode(cls.__name__))

        return p

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

        for url, ptype in cls._product_urls_and_types_wrapper([product_type]):
            logging.info('Found product URL: {0}'.format(url))
            data = (url, ptype)
            product_urls_and_types.append(data)

        logging.info('Finished getting product URL from {0} with type ' \
                    '{1}'.format(cls.__name__, product_type))

        return product_urls_and_types

    @classmethod
    def _product_urls_and_types_wrapper(cls, product_types):
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
        except Exception:
            raise StoreScrapError(traceback.format_exc().splitlines())

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
        Returns a list [name, dict] corresponding to the name and price with
        different paying methods of the product with the given URL. If the
        product is not available the dict should be empty. If not even the
        name of the product can be obtained (e.g. redirects to the homepage)
        use the URL as name.

        The returned dictionary is of the type str => Decimal, where the keys
        are the names of the payment methods avaiable (e.g. "cash") and the
        values the actual prices.

        :param url: URL of the product in the store webpage
        :type url: unicode

        :rtype: (unicode, dict)

        """

        raise NotImplementedError('The subclass of Store should implement '
                                  '_retrieve_product and Store should not be '
                                  'instantiated directly')

    @classmethod
    def product_types(cls):
        """
        Returns a list of unicodes corresponding to the product types that the
        store handles.

        :rtype: list of unicode

        """
        raise NotImplementedError('The subclass of Store should implement '
                                  'product_types and Store should '
                                  'not be instantiated directly')
