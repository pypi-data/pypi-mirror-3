#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 LShift
# All rights reserved.
#

from setuptools import find_packages, setup

setup(
    name         = 'TracEmailDigestPlugin',
    version      = '0.1',
    description  = 'Email notifications & daily digests for tickets in Trac',
    long_description = """
        LShift internal Trac plugin component to generate
        email notifications & daily digests from tickets.
    """,
    author       = 'Lee Wei',
    author_email = 'leewei@lshift.net',
    license      = 'BSD',
    url          = 'http://www.lshift.net/',
    download_url = 'http://www.lshift.net/',
    keywords     = 'trac email digest plugin',
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: Software Development :: Version Control',
    ],
    packages = find_packages(exclude=['*.tests*']),
    install_requires = [
        'setuptools>=0.6b1',
        'Trac>=0.12',
        'AMQPDeliver>=0.1',
        'TracCron>=0.3dev'
    ],
	extras_require={
		'amqpdeliver': 'AMQPDeliver',
        'traccron':    'TracCronPlugin'
	},
    entry_points = {
        'trac.plugins': [
            'notifier = notifier'
        ]
    },
    include_package_data=True,
    package_data = {
        'notifier': [
            'templates/*.html',
            'htdocs/css/*.css', 'htdocs/img/*', 'htdocs/js/*.js'
        ]
    },
    test_suite = 'notifier.tests.test_suite',
    tests_require = [],
	zip_safe = False
)
