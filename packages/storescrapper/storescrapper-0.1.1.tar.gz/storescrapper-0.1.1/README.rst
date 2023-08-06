=============
StoreScrapper
=============

StoreScrapper provides a convenient API to obtain product
information from a variety of stores. Typical usage of
the library is as follows::

    #!/usr/bin/env python

    from storescrapper.stores import Sym

    for product in Sym.products():
        print product

Features
========

* Obtain name, URL and price for many of the stores in the
  market in a straighforward way.

* Obtain only the types of products you need.

* Easily extensible with new stores and product types that
  plug-in into the existing framework.

* Leverage the power of asynchronous tasks using
  `Celery <http://celeryproject.org/>`_ to
  speed-up the scrapping process ten-fold.

* Never used Celery before? You can get up and running in
  minutes.

Installation
============

The easiest way to install storescrapper is using pip::

    pip install storescrapper

Otherwise you can download the tar.gz source, extract its 
contents and install the library directly. But first let's
make sure everything works as expected::

    python setup.py test

Don't worry if you get a TypeError exception at the end, 
just make sure all the tests pass. 

After that build and install the library (you may need 
superuser privileges for the second command)::

    python setup.py build
    python setup.py install

Using StoreScrapper in Linux
============================

1) Install the RabbitMQ server with your distribution
   package manager (Fedora yum in this case)::

    sudo yum install rabbitmq-server

   **Note for Ubuntu users: The RabbitMQ server included
   with the distribution is extremely dated and incompatible, 
   with the current version of celery / kombu.
   Install RabbitMQ from another source.**

2) Install the StoreScrapper package::

    sudo pip install storescrapper

3) In an empty directory, create a celeryconfig.py file with
   the following contents::

    BROKER_URL = 'amqp://guest:guest@localhost/'
    CELERY_RESULT_BACKEND = 'amqp'
    CELERY_IMPORTS = [
        'storescrapper.store'
        ]
    CELERYD_CONCURRENCY = 20
    CELERY_TASK_PUBLISH_RETRY = True

5) Open three terminals at the same time on this directory.
   On the first one execute::

    sudo rabbitmq-server

   On the second one execute::

    celeryd -l info

   On the third one open a Python shell and write the
   following commands to print the products from Sym::

    from storescrapper.stores.sym import Sym

    for product in Sym.products():
        print product

6) In one or two minutes this will return all of the
   products in the store with the current products types.
   You can check the progress on the shell that is running
   celeryd.