#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

import distutils.core

distutils.core.setup(
    name             = 'prego',
    version          = '0.1.1',
    author           = 'David Villa Alises',
    author_email     = 'David.Villa@gmail.com',
    packages         = ['prego'],
    data_files       = [('/usr/share/doc/prego', ['README.rst'])],
    url              = 'https://bitbucket.org/DavidVilla/prego',
    license          = 'GPLv3',
    description      = 'System test framework over POSIX shells',
    long_description = open('README.rst').read(),
    requires         = ['hamcrest', 'commodity'],
    classifiers      = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        ],
)
