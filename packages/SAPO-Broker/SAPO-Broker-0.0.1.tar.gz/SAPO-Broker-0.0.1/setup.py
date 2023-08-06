# coding=utf-8

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
from os import path

version = '0.0.1'

setup(
    name='SAPO-Broker',
    packages=find_packages(where='src'),
    package_dir = {'Broker': path.join('src', 'Broker')},
    #packages = ['Broker'],
    #py_modules = ['Broker'],
    author = 'Cláudio Valente',
    author_email = 'broker@softwarelivre.sapo.pt',
    description="SAPO Broker python client",
    long_description="""Python interface for SAPO Broker supporting 
    - Serializations
        * Protobuf
        * Thrift
    - Transports
        * TCP
        * UDP 
        * SSL
        * Dropbox""",
    url="http://softwarelivre.sapo.pt/broker/",
    #install_requires = ['iso8601'],
    install_requires = ['protobuf', 'thrift'],
    version = version,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        #'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
	    'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
