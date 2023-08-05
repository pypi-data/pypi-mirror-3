#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name = 'gitbox',
    version = '0.1.3',
    description = 'Simple and automatically sync deamon for git repositories. A dropbox alternative.',
    author = 'Christoph Jerolimov & Daniel Nuemm',
    author_email = 'christoph@jerolimov.de, daniel.nuemm@googlemail.com',
    url = 'https://github.com/monocult/gitbox',

    install_requires = ['distribute', 'urllib3', 'py-notify>=0.1.1','watchdog>=0.5.4'],

    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'gitbox  = gitbox.cli:main',
            'gitboxd = gitbox.deamon:main',
        ],
        'gui_scripts': []
    }

)
