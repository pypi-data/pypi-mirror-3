Formic: Apache Ant Globs in Python
==================================

Formic is an implementation of Apache Ant Globs in Python. The package can be
used either from the command line or as a library.

.. toctree::
   :maxdepth: 1

   installation
   globs
   api

Quickstart
----------

Formic can be installed from the Cheeseshop with easy_install or pip.
See :doc:`installation` for more options::

   $ easy_install formic

Once installed, you can use Formic either from the command line, eg::

   $ formic -i "*.py" -e "__init__.py" "**/*test*/" "test_*"

Or integrated right into your Python 2.7 project, eg::

    import formic
    fileset = formic.FileSet(include="**.py",
                             exclude=["**/*test*/**", "test_*"]
                             )

    for file_name in fileset.qualified_files():
        # Do something with file_name
        ...

That's about it :)

Slightly more detail
====================

Ant Globs
---------

A :mod:`~formic.formic` contains the file search algorithm which is accessed
using :class:`~formic.formic.FileSet`. The algorithm works by scanning
an entire directory tree from a start-point; within each directory it:

1. **Includes** files from one or more Ant Globs, then
2. Optionally **excludes** files matching further Ant Globs.

Ant Globs are a superset of ordinary file system globs. The key differences:

* They match whole paths, eg ``/root/myapp/*.py``
* \*\* matches *any* directory or *directories*, eg ``/root/**/*.py`` matches
  ``/root/one/two/my.py``
* You can match the topmost directory or directories, eg ``/root/**``, or
* The parent directory of the file, eg ``**/parent/*.py``, or
* Any parent directory, eg ``**/test/**/*.py``

For example, one Ant Glob might match one type of file in one location, while
a second matches a *different* type somewhere else.

Ant, and Formic, has a set of *default excludes*. These are files and
directories that, by default, are automatically excluded from all searches.
The majority of these are files and directories related to VCS (eg .svn
directories).

More information can be found at :doc:`globs`

Command Line
------------

The :command:`formic` command provides shell access to Ant glob functionality. Some
examples are shown below

Find all Python files under ``myapp``::

    $ formic myapp -i "*.py"

(Note that if a root directory is specified, it must come before the -i or -e)

Find all Python files under the current directory, but exclude ``__init__.py``
files::

    $ formic -i "*.py" -e "__init__.py"

... and further refined by removing test directories and files::

    $ formic -i "*.py" -e "__init__.py" "**/*test*/" "test_*"

Output from :command:`formic` is formatted like the Unix :command:`find` command,
and so can easily be combined with other executables, eg::

    $ formic -i "**/*.bak" | xargs rm

... will delete all ``.bak`` files in or under the current directory (but excluding
VCS directories such as ``.svn`` and ``.hg``).

Full usage is documented in :mod:`formic.command`.

Library
-------

The API provides the same functionality as the command-line but in a form
more readily consumed by applications which need to gather collections of files
efficiently.

The API is quite simple for normal use. The example below will gather all the
Python files in and under the current working directory, but exclude all
directories which contain 'test' in their name, and all files whose name
starts with 'test\_'::

    import formic
    fileset = formic.FileSet(include="**.py",
                             exclude=["**/*test*/**", "test_*"]
                             )

    for file_name in fileset.qualified_files():
        # Do something with file_name
        ...

The functionality is described in :class:`~formic.formic.FileSet`. For more detailed
usage, the API is documented :doc:`api`:

About Formic
============

Formic is written and maintained by Andrew Alcock (formic@aviser.asia)
of Aviser LLP, Singapore. The Home Page is:

* http://www.aviser.asia/formic

Source code and issue tracker are hosted on BitBucket:

* https://bitbucket.org/aviser/formic

Formic is Copyright (C) 2012, Aviser LLP and released under
`GPLv3 <http://www.gnu.org/licenses/gpl.html>`_. Aviser LLP would be happy to
discuss other licensing arrangements; for details, please email the maintainer.
