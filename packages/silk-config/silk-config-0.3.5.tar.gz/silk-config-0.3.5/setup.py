#!/usr/bin/python
from setuptools import setup, find_packages

setup(
    name='silk-config',
    version='0.3.5',
    author='Brent Tubbs',
    author_email='brent.tubbs@gmail.com',
	packages=find_packages(),
    include_package_data=True,
	install_requires = [
        'PyYAML',
	],
    url='http://bits.btubbs.com/silk-config',
    license='LICENSE.txt',
    description=('Small package for reading and returning the configuration of '
                 'a Silk-configured site'),
)

