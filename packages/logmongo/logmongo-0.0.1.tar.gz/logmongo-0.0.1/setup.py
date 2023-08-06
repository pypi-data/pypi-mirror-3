# installation: easy_install logmongo

from setuptools import setup

requires = [
    'pymongo',
    'prettyprint',
]

setup( 
    name = 'logmongo',
    version = '0.0.1',
    description = 'Logmongo: Log messages to a capped MongoDB collection',
    keywords = 'Logmongo log dict messages mongo MongoDB',
    long_description = open('README').read(),

    author = 'Russell Ballestrini',
    author_email = 'russell@ballestrini.net',
    url = 'https://bitbucket.org/russellballestrini/logmongo',

    platforms = ['All'],
    license = 'Public Domain',

    py_modules = ['logmongo'],
    include_package_data = True,

    install_requires = requires,
)

# setup keyword args: http://peak.telecommunity.com/DevCenter/setuptools

# built and uploaded to pypi with this:
# python setup.py sdist bdist_egg register upload
