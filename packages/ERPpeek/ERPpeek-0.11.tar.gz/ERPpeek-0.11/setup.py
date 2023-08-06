#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement

from setuptools import setup


def get_version(source='erppeek.py'):
    with open(source) as f:
        for line in f:
            if line.startswith('__version__'):
                return eval(line.split('=')[-1])

with open('README.rst') as f:
    readme = f.read()

# with open('CHANGES.rst') as f:
#     readme += '\n\n\n' + f.read()

setup(
    name='ERPpeek',
    version=get_version(),
    license='BSD',
    description='Versatile tool for browsing OpenERP data',
    long_description=readme,
    url='http://erppeek.readthedocs.org/',
    author='Florent Xicluna',
    author_email='florent.xicluna@gmail.com',
    py_modules=['erppeek'],
    zip_safe=False,
    platforms='any',
    entry_points={
        'console_scripts': [
            'erppeek = erppeek:main',
        ]
    },
    keywords="openerp xml-rpc xmlrpc",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
