# -*- coding: utf-8 -*-
import os
from distutils.core import setup

setup(
    name             = 'pyselenese2',
    version          = '0.1.0',
    description      = "Python Selenese translator",
    author           = 'Esteban Ordano',
    author_email     = 'eordano@gmail.com',
    url              = 'https://github.com/eordano/pyselenese2',
    license          = 'MIT License',
    long_description = open('README.rst').read(),
    packages         = ['pyselenese2'],
    classifiers      = [
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Testing',
    ],
)
