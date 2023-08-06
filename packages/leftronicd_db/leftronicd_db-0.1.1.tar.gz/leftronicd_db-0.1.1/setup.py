#!/usr/bin/env python
# -*- coding: utf-8 -*-
from leftronicd import __version__
from setuptools import setup, find_packages


INSTALL_REQUIRES = [
    'PyYAML==3.10',
    'Twisted==12.0.0',
    'certifi==0.0.8',
    'chardet==1.0.1',
    'leftronic==1.4',
    'pyOpenSSL==0.13',
    'requests==0.11.1',
    'wsgiref==0.1.2',
    'zope.interface==3.8.0',
#    'MySQL-python==1.2.3',
    'SQLAlchemy==0.7.7',
#    'pyodbc==3.0.3',
    # remove database-specific driver packages; those should be installed separately with pip
]

try:
    import json
except ImportError:
    INSTALL_REQUIRES.append('simplejson')

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development',
]

setup(
    name='leftronicd_db',
    version='0.1.1',
    description='A twisted based daemon to send metrics to leftronic.com',
    author='Jonas Obrist, Henry Barnor',
    author_email='ojiidotch@gmail.com, henry@leftronic.com',
    url='https://github.com/sonofabell/leftronicd',
    packages=find_packages(),
    license='BSD',
    platforms=['OS Independent'],
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    entry_points="""
    [console_scripts]
    leftronicd = leftronicd.main:cli
    """,
)
