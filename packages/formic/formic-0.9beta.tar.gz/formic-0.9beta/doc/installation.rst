Installing Formic
=================

Prequisites
-----------

Platform and dependencies: Formic requires Python 2.7; it has been tested on
Mac OS X, Ubuntu and Windows. As long as Python works, it should work on most
versions of these platforms. Formic has no dependencies outside the Python
system libraries.

Installation options
--------------------

There are three ways to obtain Formic shown below, in increasing difficulty
and complexity. You need only pick one:

**Option 1: Automated install**

Simplest: use::

    $ easy_install formic

or::

    $ pip install formic

**Option 2: Source install**

To download the source package and install from that:

First, download the appropriate package from Formics page on the `Python
Package Index <http://pypi.python.org/pypi/formic>`_. This is a GZipped TAR
file.

Next, extract the package using your preferred GZip utility.

Finally, navigate into the extracted directory and perform the installation::

    $ python setup.py install

**Option 3: Check out the project**

If you like, you could download the source and compile it yourself. The
source is on a Mercurial DVCS at https://bitbucket.org/aviser/formic.
BitBucket provides great instructions to perform this activity.

After checking out the source, navigate to the top level directory::

    $ python setup.py install

Validating the installation
---------------------------

After installing, you should be able to execute Formic from the command line::

    $ formic --version
    formic 0.9beta http://www.aviser.asia/formic

If you downloaded the source, you can additionally run the unit tests. This
requires py.test::

    $ easy_install pytest
    $ cd formic
    $ py.test
    ========================== test session starts ==========================
    platform darwin -- Python 2.7.1 -- pytest-2.2.3
    collected 40 items

    test_formic.py ........................................

    ======================= 40 passed in 2.55 seconds =======================
