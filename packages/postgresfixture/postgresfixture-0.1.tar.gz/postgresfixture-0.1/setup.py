#!/usr/bin/env python
# Copyright 2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Distutils installer for postgresfixture."""

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    )

__metaclass__ = type

from setuptools import setup


with open("requirements.txt", "rb") as fd:
    requirements = {line.strip() for line in fd}


setup(
    name='postgresfixture',
    version="0.1",
    packages={b'postgresfixture'},
    package_dir={'postgresfixture': 'postgresfixture'},
    install_requires=requirements,
    tests_require={"testtools >= 0.9.14"},
    test_suite="postgresfixture.tests",
    include_package_data=True,
    zip_safe=False,
    description=(
        "A fixture for creating PostgreSQL clusters and databases, and "
        "tearing them down again, intended for use during development "
        "and testing."),
    entry_points={
        "console_scripts": [
            "postgresfixture = postgresfixture.main:main",
            ],
        },
    )
