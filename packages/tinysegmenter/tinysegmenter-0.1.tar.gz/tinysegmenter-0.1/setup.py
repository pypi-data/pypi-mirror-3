#!/usr/bin/python
# -*- coding: utf-8 -*-

import distutils.core
import sys

try:
    long_description_fd = open('README.rst', 'r')
    long_description = long_description_fd.read().rstrip(' \n\t\r')
    long_description_fd.close()
except IOError:
    sys.exit('README.rst file not found. Are you not running this script from the source root directory?')

distutils.core.setup(
    name = 'tinysegmenter',
    version = '0.1',
    author = 'Taku Kudo',
    author_email = 'taku at chasen.org',
    url = 'http://lilyx.net/tinysegmenter-in-python/',
    maintainer = 'Jehan',
    maintainer_email = 'jehan at gengo.com',
    description = 'Very compact Japanese tokenizer',
    long_description = long_description,
    license = 'New BSD',
    package_dir = {'': 'src'},
    py_modules = ['tinysegmenter'],
    classifiers = [
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Operating System :: POSIX :: Linux',
        'Development Status :: 4 - Beta',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Text Processing :: Linguistic'
    ],
)
