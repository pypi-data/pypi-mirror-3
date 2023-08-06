# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup, find_packages

import os
import sys
from distutils import log

long_desc = ''' '''
requires = ['numpy', 'fluid']

setup(
    name='maud',
    version='0.4',
    url='https://bitbucket.org/castelao/pyunevenwindowmean',
    download_url='https://bitbucket.org/castelao/pyunevenwindowmean',
    license='PSF',
    author='Guilherme Castelao, Bia Villas-Boas, Luiz Irber, Roberto de Almeida',
    author_email='guilherme@castelao.net, bia@melovillasboas.com, luiz.irber@gmail.com, roberto@dealmeida.net',
    description='Moving Average for Uneven Data',
    long_description=long_desc,
    zip_safe=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    platforms='any',
    py_modules=['maud', 'window_func'],
    packages=find_packages(),
    install_requires=requires,
)
