#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from asv_files import __name__, __version__, __keywords__, __description__

##
## To deploy use
## $ python ./setup.py sdist upload
##
## Your need increase version before it !!!
##

packages  = find_packages()
setup(
    name = __name__,
    version = __version__,
    packages = packages,
    include_package_data = True,

    install_requires = [
        'asv_utils>=dev-20120401-01',
        'asv_media>=dev-20120501-01',
    ],
    setup_requires = [
        'distribute>=0.6',
    ],

    author       = 'Sergey Vasilenko',
    author_email = 'sv@makeworld.ru',
    keywords  = __keywords__,
    description  = open('README.txt').read(),
    long_description = open('README.txt').read(),
    license   = 'GPL',
    platforms = 'All',
    url  = 'http://bitbucket.org/xenolog/{}/wiki/Home'.format(__name__),

    classifiers = [
        'Environment :: Other Environment',
        'Framework :: Django',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Natural Language :: Russian',
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Libraries',
    ],
    zip_safe = False,
)


