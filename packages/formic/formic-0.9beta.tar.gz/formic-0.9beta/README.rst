Formic: Apache Ant Globs in Python
==================================

Formic is an implementation of Apache Ant Globs in Python. The package can be
used either from the command line or as a library.

Quickstart
----------

Formic can be installed from the Cheeseshop with easy_install or pip.::

   $ easy_install formic

Once installed, you can use Formic either from the command line::

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

Ant Globs
---------

A FileSet contains an advanced algorithm to select
files in a specific directory tree. The algorithm has two parts:

1. **Include** files matching one or more Ant Globs,
2. Optionally **exclude** files matching further Ant Globs.

Ant Globs are a superset of ordinary file system globs. The key differences:

* They match whole paths, eg ``/root/myapp/*.py``
* \*\* matches *any* directory or *directories*, eg ``/root/**/*.py`` matches
  ``/root/one/two/my.py``
* You can match the topmost directory or directories, eg ``/root/**``, or
* The parent directory of the file, eg ``**/parent/*.py``, or
* Any parent directory, eg ``**/test/**/*.py``

Command Line
------------

The ``formic`` command provides shell access to Ant glob functionality. Some
examples are shown below

Find all Python files under ``myapp``::

    $ formic myapp -i "*.py"

(Note that if a root directory is specified, it must come before the -i or -e)

Find all Python files under the current directory, but exclude ``__init__.py``
files::

    $ formic -i "*.py" -e "__init__.py"

... and further refined by removing test directories and files::

    $ formic -i "*.py" -e "__init__.py" "**/*test*/" "test_*"

Output from ``formic`` is formatted like the Unix ``find`` command,
and so can easily be combined with other executables, eg::

    $ formic -i "**/*.bak" | xargs rm

... will delete all ``.bak`` files in or under the current directory (but excluding
VCS directories such as ``.svn`` and ``.hg``).


Library
-------

The API provides the same functionality as the command-line but in a form
more readily consumed by applications that need to gather collections of files
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

About Formic
------------

Formic is written and maintained by Andrew Alcock (formic@aviser.asia)
of Aviser LLP, Singapore. The Home Page is:

* http://www.aviser.asia/formic

Source code and issue tracker are hosted on BitBucket:

* https://bitbucket.org/aviser/formic

Formic is Copyright (C) 2012, Aviser LLP and released under
`GPLv3 <http://www.gnu.org/licenses/gpl.html>`_. Aviser LLP would be happy to
discuss other licensing arrangements; for details, please email the maintainer.
