Changelog
=========

0.9beta3
--------

* API: FileSet is now a natural iterator::

    fs = FileSet(include="*.py")
    filenames = [ filename for filename in fs ]

* API: ``__str__()`` on Pattern and FileSet has been improved. Pattern now
  returns the just normalized string for the pattern (eg ``**/*.py``). FileSet
  now returns the details of the set include all the include and exclude
  patterns.

* Setup: Refactored setup.py and configuration to use only setuptools (removing
  distribute and setuptools_hg)

* Documentation: Renamed all ReStructured Text files to .rst. Small
  improvements to installation instructions.


0.9beta2
--------

* Refactored documentation files and locations to be more DRY:

  * Sphinx documentation
  * setup.py/Pypi readme
  * README/INSTALL/CHANGELOG/USAGE in topmost directory

* Removed the file-based distribute depending on explicit dependency
  in setup.py

0.9beta
-------

Date: 14 Apr 2011
First public release