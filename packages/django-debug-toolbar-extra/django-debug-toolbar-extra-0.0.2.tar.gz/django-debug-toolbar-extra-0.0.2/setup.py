# Copyright (c) 2010 by Yaco Sistemas <pmartin@yaco.es>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

import os
from setuptools import setup


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name="django-debug-toolbar-extra",
    version="0.0.2",
    author="Yaco Sistemas S.L.",
    author_email="pmartin@yaco.es",
    description="Django application that allows add funcionality to the django-debug-toolbar",
    long_description=(read('README') + '\n\n' + read('CHANGES')),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    ],
    license="LGPL 3",
    keywords="django,debug toolbar,debug,toolbar,panels",
    url='https://tracpub.yaco.es/djangoapps/wiki/DjangoDebugToolbarExtra',
    packages=('debug_toolbar_extra',),
    include_package_data=True,
    zip_safe=False,
)
