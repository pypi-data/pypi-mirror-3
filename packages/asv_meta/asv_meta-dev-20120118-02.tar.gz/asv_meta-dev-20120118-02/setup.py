#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

__name__ = 'asv_meta'
__version__ = 'dev-20120118-02'
__keywords__ = 'django asv'
__description__ = '''
This is a metapackage for quick installing other asv_* packages.
'''

##
## To deploy use
## $ python ./setup.py sdist upload
##
## Your need increase __version__ before it !!!
##
                  
packages  = find_packages()
setup(
    name = __name__,
    version = __version__,
    packages = packages,
    include_package_data = True,

    install_requires = [
        'pytils>=0.2.3',
        'asv-imgs>=dev-20111110-01',
        'asv-seo>=dev-20110720-01',
        'asv-txt>=dev-20110709-01',
        'asv-utils>=dev-20120115-02',
    ],
    setup_requires = [
        'distribute>=0.6',
    ],

    author       = 'Sergey Vasilenko',
    author_email = 'sv@makeworld.ru',
    keywords  = __keywords__,
    description  = __description__,
    long_description = open('README.txt').read(),
    license   = 'GPL',
    platforms = 'All',
    url  = 'http://bitbucket.org/xenolog/{}/wiki/Home'.format(__name__),

    classifiers = [
        'Environment :: Other Environment',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Natural Language :: Russian',
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Libraries',
    ],
    zip_safe = False,
)


