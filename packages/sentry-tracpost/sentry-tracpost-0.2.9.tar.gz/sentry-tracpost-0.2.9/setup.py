#!/usr/bin/env python
"""
sentry-tracpost
==============

An extension for Sentry which integrates with Trac. It will send Trac tickets over XML RPC.

:copyright: (c) 2012 by Josh Harwood.
:license: BSD, see LICENSE for more details.
"""
from setuptools import setup, find_packages


tests_require = [
    'nose>=1.1.2',
]

install_requires = [
    'sentry>=4.6.0',
]

setup(
    name='sentry-tracpost',
    version='0.2.9',
    author='Josh Harwood',
    author_email='jharwood@joinerysoft.com',
    url='',
    description='A Sentry extension which integrates with Trac',
    long_description=__doc__,
    license='BSD',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='runtests.runtests',
    entry_points={
       'sentry.plugins': [
            'tracpost = sentry_tracpost.plugin:TracPost'
        ],
       'sentry.apps': [
	    'tracpost = sentry_tracpost.plugin:TracPost'
	],
    },
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
