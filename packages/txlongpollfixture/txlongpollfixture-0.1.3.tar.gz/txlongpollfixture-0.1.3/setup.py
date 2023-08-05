#!/usr/bin/env python
"""Distutils installer for txlongpollfixture."""

from setuptools import setup, find_packages


setup(
    name='txlongpollfixture',
    version="0.1.3",
    packages=find_packages('.'),
    package_dir={'': '.'},
    include_package_data=True,
    zip_safe=False,
    maintainer='Launchpad Developers',
    description='A test fixture for txlongpoll.',
    license='Affero GPL v3',
    install_requires=[
        'fixtures >= 0.3.6',
        'setuptools',
        'testtools >= 0.9.11',
        # txlongpoll is not required here because we don't import it anywhere.
        # It should be set up in the PATH so the fixture can Popen() it.
        ],
    extras_require=dict(
        test=[
            'txlongpoll >= 0.2.8',
            # txlongpoll included here so that PATH doesn't have to be set to
            # make the fixture's tests pass.
            ],
        ))
