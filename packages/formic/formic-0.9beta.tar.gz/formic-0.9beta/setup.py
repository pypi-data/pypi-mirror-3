###############################################################################
# Formic: An implementation of Apache Ant FileSet globs
# Copyright (C) 2012, Aviser LLP, Singapore.
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
###############################################################################

import distribute_setup
distribute_setup.use_setuptools()
from os import path
from setuptools import setup, find_packages

def read(fname):
    return open(path.join(path.dirname(__file__), fname)).read()

README = """Formic: Apache Ant Globs in Python
==================================

Formic is an implementation of Apache Ant Globs in Python. The package can be
used either from the command line or as a library.

Quickstart
----------

Formic can be installed from the Cheeseshop with easy_install or pip.:

   $ easy_install formic

Once installed, you can use Formic either from the command line:

   $ formic -i "*.py" -e "__init__.py" "**/*test*/" "test_*"

Or integrated right into your Python 2.7 project::

    import formic
    fileset = formic.FileSet(include="**.py",
                             exclude=["**/*test*/**", "test_*"]
                             )

    for file_name in fileset.qualified_files():
        # Do something with file_name
        ...

That's about it :)

More detailed instructions and API documentation are available at
http://www.aviser.asia/formic

About Formic
------------

Formic is written and maintained by Andrew Alcock (formic@aviser.asia)
of Aviser LLP, Singapore.

Formic is Copyright (C) 2012, Aviser LLP and released under
`GPLv3 <http://www.gnu.org/licenses/gpl.html>`_. Aviser LLP would be happy to
discuss other licensing arrangements; for details, please email the maintainer.
"""

setup(
    name='formic',
    version=read(path.join("formic", "VERSION.txt")),
    description='An implementation of Apache Ant FileSet globs',
    long_description=README,
    author='Aviser LLP, Singapore',
    author_email='formic@aviser.asia',
    url='http://www.aviser.asia/formic',
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        ],
    keywords='Apache Ant, glob, FileSet, file utilities, find',
    license='GPLv3+',

    # The main definition of the installer
    setup_requires=['setuptools_hg'],
    packages=find_packages(),
    zip_safe = True,

    entry_points = {
            'console_scripts': [
                'formic  = formic.command:entry_point'
            ],
        },
)

