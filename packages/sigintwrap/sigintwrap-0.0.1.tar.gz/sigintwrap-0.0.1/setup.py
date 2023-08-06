#!/usr/bin/env python
from setuptools import setup, find_packages
import versiontools_support
from sys import version

if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None
setup(name = 'sigintwrap',
        version = ':versiontools:sigintwrap',
        description = 'Wrapper to forward TERM signals to INT signals so uWSGI plays nice with runit',
        author = 'Josh Bryan',
        author_email = 'jbryan@ci.uchicago.edu',
        url = 'https://globusonline.github.com/sigint',
        packages = find_packages(),
        classifiers = [
              'Programming Language :: Python :: 2',
           ],

        entry_points = {
            'console_scripts': ['sigintwrap = sigintwrap.sigintwrap:main']
            }
        )
