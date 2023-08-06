#!/usr/bin/env python
# Copyright 2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Distutils installer for saucelabsfixture."""

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
    name='saucelabsfixture',
    version="0.1",
    packages={b'saucelabsfixture'},
    package_dir={'saucelabsfixture': 'saucelabsfixture'},
    install_requires=requirements,
    tests_require={"testtools >= 0.9.14"},
    test_suite="saucelabsfixture.tests",
    include_package_data=True,
    zip_safe=False,
    description="A fixture for working with SauceLabs' services.",
    )
