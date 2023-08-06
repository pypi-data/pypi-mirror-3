from setuptools import setup

# We add the path to the tests so that the celeryconfig.py file may be found
import sys
sys.path.append('storescrapper/tests')

setup(
    name='storescrapper',
    version='0.1.1',
    author='Vijay Khemlani',
    author_email='vkhemlan@gmail.com',
    packages=[
        'storescrapper',
        'storescrapper.stores',
        'storescrapper.exceptions',
        'storescrapper.tests'
    ],
    scripts=[],
    url='http://www.solotodo.net/',
    license='LICENSE.txt',
    description='Web scrapping API for selected stores',
    long_description=open('README.rst').read(),
    tests_require=[
        'nose>=1.1.2'
    ],
    test_suite='nose.collector',
    install_requires=[
        'mechanize>=0.2.5',
        'BeautifulSoup>=3.2.0',
        'kombu>=2.0.0',
        'celery>=2.4.6',
        ],
)
