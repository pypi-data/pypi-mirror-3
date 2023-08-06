from setuptools import setup, find_packages
import os

_home = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Products', 'PloneGlossary')

version = open(os.path.join(_home, 'version.txt')).read().strip()
long_description = open(os.path.join(_home, "README.txt")).read() + "\n\n"
long_description += open(os.path.join(_home, "CHANGES")).read()
long_description = long_description.decode('utf8')

setup(
    name='Products.PloneGlossary',
    version=version,
    long_description=long_description,
    description="Hilite Plone content terms, mouseover shows the term definition as tooltip.",
    # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Framework :: Plone :: 3.2",
        "Framework :: Plone :: 3.3",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    keywords='plone glossary',
    author='Ingeniweb',
    author_email='support@ingeniweb.com',
    url='http://plone.org/products/ploneglossary',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['Products'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'wicked',
        ],
    entry_points="""
    # -*- Entry points: -*-
    """,
    )
