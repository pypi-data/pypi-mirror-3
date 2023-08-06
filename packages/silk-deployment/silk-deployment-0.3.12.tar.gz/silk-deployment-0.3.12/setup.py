#!/usr/bin/python
from setuptools import setup, find_packages

setup(
    name='silk-deployment',
    version='0.3.12',
    author='Brent Tubbs',
    author_email='brent.tubbs@gmail.com',
	packages=find_packages(),
    package_dir={'silk': 'silk'},
    include_package_data=True,
    entry_points = {
        'console_scripts': [
            'silk = silk.lib:cmd_dispatcher',
        ],
    },
	install_requires = [
        'gunicorn',
        'CherryPy',
        'Fabric >= 1.0.1',
        'PyYAML',
        'silk-config>=0.3.3,<0.4',
	],
    url='http://bits.btubbs.com/silk-deployment',
    license='LICENSE.txt',
    description='A Fabric-based tool for deploying WSGI apps on an Ubuntu/Nginx/Supervisord/Gunicorn stack.',
    #long_description=open('README.rst').read(),
)

