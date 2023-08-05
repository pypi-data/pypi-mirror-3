# tranchitella.adyen
# Copyright (C) 2008-2010 Tranchitella Kft. <http://tranchtella.eu>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Library General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from setuptools import setup, find_packages

install_requires = [
    'setuptools',
    'ZSI',
]

setup(
    name='tranchitella.adyen',
    version='0.3',
    url='http://pypi.python.org/pypi/tranchitella.adyen',
    license='LGPL 2',
    author='Tranchitella Kft.',
    author_email='info@tranchitella.eu',
    description="Interface to the Adyen payment gateway",
    long_description=(
        open('README.txt').read() + '\n\n' +
        open('CHANGES.txt').read()
    ),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['tranchitella'],
    install_requires=install_requires,
    include_package_data=True,
    zip_safe=False,
)
