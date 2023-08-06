#!/usr/bin/env python
"""
raven-sanitize-openerp
======================

Sanitize[1] data for sentry from OpenERP stacktraces.

[1] http://raven.readthedocs.org/en/latest/config/index.html#processors
"""

from setuptools import setup, find_packages

install_requires = [
    'raven',
]

setup(
    name='raven-sanitize-openerp',
    version='0.1.1',
    author='GISCE-TI, SL',
    author_email='devel@gisce.net',
    url='http://code.gisce.net/raven-sanitize-openerp',
    description='Sanitize data for sentry from OpenERP stacktraces',
    long_description=__doc__,
    packages=find_packages(),
    zip_safe=False,
    install_requires=install_requires,
    test_suite='runtests.runtests',
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
