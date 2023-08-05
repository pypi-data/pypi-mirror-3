#!/usr/bin/env python

# Copyright (c) 2012 Linaro
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages


setup(
    name='gator-tests',
    version=":versiontools:gator_tests:",
    author='David Stubbs',
    author_email='david.stubbs2@arm.com',
    url='https://code.launchpad.net/~stubbsdm/+junk/gator-tests',
    description='Tests for checking the gator module and gator daemon',
    long_description=open("README").read(),
    packages=find_packages(),
    license="GNU GPLv3",
    entry_points="""
    [lava_test.test_definitions]
    gatormodule = gator_tests.modulecheck
    """,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Testing",
    ],
    install_requires=[
        'lava-test >= 0.2',
        'versiontools >= 1.8',
    ],
    setup_requires=[
        'versiontools >= 1.8'
    ],
    zip_safe=False,
    include_package_data=True)
