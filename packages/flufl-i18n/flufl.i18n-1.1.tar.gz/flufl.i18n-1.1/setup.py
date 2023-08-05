# Copyright (C) 2009-2012 by Barry A. Warsaw
#
# This file is part of flufl.i18n
#
# flufl.i18n is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, version 3 of the License.
#
# flufl.i18n is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with flufl.i18n.  If not, see <http://www.gnu.org/licenses/>.

from distribute_setup import use_setuptools
use_setuptools()

from setup_helpers import (
    description, get_version, long_description, require_python)
from setuptools import setup, find_packages


require_python(0x20600f0)
__version__ = get_version('flufl/i18n/__init__.py')


setup(
    name='flufl.i18n',
    version=__version__,
    namespace_packages=['flufl'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    maintainer='Barry Warsaw',
    maintainer_email='barry@python.org',
    description=description('README.rst'),
    long_description=long_description(
        'flufl/i18n/README.rst',
        'flufl/i18n/NEWS.rst'),
    license='LGPLv3',
    url='https://launchpad.net/flufl.i18n',
    download_url='https://launchpad.net/flufl.i18n/+download',
    test_suite='flufl.i18n.tests',
    )
