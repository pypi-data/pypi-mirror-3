import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup
import sys

# Python 3 conversion
extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(
    name = 'Keen-SoftLayer',
    version = '1.1',
    description = "A library to contact SoftLayer's backend services",
    author = 'SoftLayer Technologies, Inc.',
    author_email = 'dan@keen.io',
    packages = [
        'SoftLayer',
    ],
    license = 'The BSD License',
    url = 'http://github.com/softlayer/softlayer-api-python-client',
    classifiers = [],
    **extra
)
