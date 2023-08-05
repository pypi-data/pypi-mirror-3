from setuptools import setup, find_packages
import sys

from Products.ZSPARQLMethod import __version__ as version

install_requires = ['sparql-client']
if sys.version_info < (2, 6):
    install_requires += ['simplejson']

docs = open('README.rst').read() + "\n\n" + open('CHANGES.rst').read()

setup(
    name='Products.ZSPARQLMethod',
    version=version,
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    license="Mozilla Public License 1.1",
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Zope2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
    ],
    description="Zope product for making SPARQL queries, simiar to ZSQLMethod",
    long_description=docs,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
)
