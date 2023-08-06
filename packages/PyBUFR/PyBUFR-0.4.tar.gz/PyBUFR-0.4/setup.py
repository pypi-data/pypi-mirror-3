# -*- coding: utf-8 -*-
RELEASE = True

try:
    from setuptools import setup, find_packages
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup, find_packages

import os
import sys
from distutils import log


version = '0.4'

long_desc = ''' '''

setup(
    name='PyBUFR',
    version=version,
    description='Pure Python library to encode and decode BUFR.',
    long_description=long_desc,
    url='https://bitbucket.org/castelao/pybufr',
    download_url = "http://cheeseshop.python.org/packages/source/P/PyBUFR/PyBUFR-%s.tar.gz" % version,
    license='PSF',
    py_modules=['bufr'],
    author='Guilherme Castelao, Roberto de Almeida, Luiz Irber',
    author_email='guilherme@castelao.net, roberto@dealmeida.net, luiz.irber@gmail.com',
    zip_safe=True,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
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
    scripts=["bin/bufrdump"],
    #packages=find_packages(),
    package_data={
        'PyBUFR': ['data/bufrtables/*.TXT', 'descriptors/*.txt'],
    },
    #include_package_data=True,
    #zip_safe=True,
    test_suite = 'nose.collector',
    install_requires=['numpy',],
)



