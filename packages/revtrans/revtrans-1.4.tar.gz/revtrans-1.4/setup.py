#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import revtrans

setup(
    name='revtrans',
    version='1.4',
    description='revtrans - performs a reverse translation of a peptide alignment',
    url='http://pypi.python.org/pypi/revtrans',
    author='Rasmus Wernersson',
    email='raz@cbs.dtu.dk',
    packages=['revtrans', ],
    license='GNU General Public License 2',
    long_description=revtrans.__doc__,
    entry_points={
        'console_scripts': [
            'revtrans = revtrans:main',
        ],
    },
)
