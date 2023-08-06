# -*- coding: utf-8 -*-
#quckstarted Options:
#
# sqlalchemy: True
# auth:       sqlalchemy
# mako:       False
#
#

import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='releasetools',
    version='0.1',
    description='A set of tools and helper scripts to make managing a release process easier',
    author='Michael J. Pedersen',
    author_email='m.pedersen@icelus.org',
    url='https://github.com/pedersen/releasetools',
    install_requires=[
        'basketweaver',
        'certifi',
        'oauth2',
        'virtualenv',
        'yolk',
        ],
    setup_requires=[],
    paster_plugins=[],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=[],
    package_data={'releasetools': []},
    message_extractors={'releasetools': []},

    entry_points={
        'console_scripts': [
            'tracker = releasetools.tracker.main:main',
            ]
        },
    zip_safe=True
)
