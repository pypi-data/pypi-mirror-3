#   Convoy is a WSGI app for loading multiple files in the same request.
#   Copyright (C) 2010-2012  Canonical, Ltd.
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
from distutils.core import setup

# If setuptools is present, use it to find_packages(), and also
# declare our dependency on epsilon.
extra_setup_args = {}
try:
    from setuptools import find_packages
    extra_setup_args = {
        'install_requires': ['Paste'],
        'tests_require': ['nose', 'mocker']
        }
except ImportError:
    def find_packages(exclude=None):
        """
        Compatibility wrapper.

        Taken from storm setup.py.
        """
        packages = []
        for directory, subdirectories, files in os.walk("convoy"):
            if '__init__.py' in files:
                packages.append(directory.replace(os.sep, '.'))
        return packages

setup(
    name="convoy",
    version="0.2.3",
    description="A combo WSGI application for use with YUI",
    author="Canonical Javascripters",
    url="https://launchpad.net/convoy",
    license="AGPL",
    packages=find_packages(exclude=('convoy.tests',)),
    include_package_data=True,
    zip_safe=False,
    test_suite="nose.collector",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
       ],
    **extra_setup_args
    )

