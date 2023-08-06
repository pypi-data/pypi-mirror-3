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

"""The command-line glue-code for :command:`formic`. Call :func:`~formic.command.main()`
with the command-line arguments.

Full usage of the command is::

  usage: formic [-i [INCLUDE [INCLUDE ...]]] [-e [EXCLUDE [EXCLUDE ...]]]
               [--no-default-excludes] [--no-symlinks] [-r] [-h] [--usage]
               [--version]
               [directory]

  Search the file system using Apache Ant globs

  Directory:
    directory             The directory from which to start the search (defaults
                          to current working directory)

  Globs:
    -i [INCLUDE [INCLUDE ...]], --include [INCLUDE [INCLUDE ...]]
                          One or more Ant-like globs in include in the search.If
                          not specified, then all files are implied
    -e [EXCLUDE [EXCLUDE ...]], --exclude [EXCLUDE [EXCLUDE ...]]
                          One or more Ant-like globs in include in the search
    --no-default-excludes
                          Do not include the default excludes
    --no-symlinks         Do not include symlinks

  Output:
     -r, --relative       Print file paths relative to directory.

  Information:
    -h, --help            Prints this help and exits
    --usage               Prints additional help on globs and exits
    --version             Prints the version of formic and exits

"""

from argparse import ArgumentParser, SUPPRESS, RawDescriptionHelpFormatter
from sys import argv, stdout
from os import path
from pkg_resources import resource_string
from formic import FileSet, FormicError, get_version, __doc__ as usage

DESCRIPTION = """Search the file system using Apache Ant globs"""

EPILOG = \
"""For documentation, source code and other information, please visit:
http://www.aviser.asia/formic

This program comes with ABSOLUTELY NO WARRANTY. See license for details.

This is free software, and you are welcome to redistribute it
under certain conditions; for details, run
> formic --license

Formic is Copyright (C) 2012, Aviser LLP, Singapore"""

def create_parser():
    """Creates and returns the command line parser, an
     :class:`argparser.ArgumentParser` instance."""
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                            description=DESCRIPTION,
                            epilog=EPILOG,
                            add_help=False)

    directory = parser.add_argument_group("Directory")
    directory.add_argument(dest='directory', action="store", default=None, nargs="?",
                           help="The directory from which to start the search "
                                "(defaults to current working directory)")

    globs = parser.add_argument_group("Globs")
    globs.add_argument('-i', '--include', action="store", nargs="*",
                           help="One or more Ant-like globs in include in the search."
                                "If not specified, then all files are implied")
    globs.add_argument('-e', '--exclude', action="store", nargs="*",
                           help="One or more Ant-like globs in include in the search")
    globs.add_argument('--no-default-excludes', dest="default_excludes",
                       action="store_false", default=True,
                       help="Do not include the default excludes")
    globs.add_argument('--no-symlinks', action="store_true", default=False,
                       help="Do not include symlinks")


    output = parser.add_argument_group("Output")
    output.add_argument('-r', '--relative', action="store_true", default=False,
                        help="Print file paths relative to directory.")


    info = parser.add_argument_group("Information")
    info.add_argument('-h', '--help', action='store_true', default=False,
                      help="Prints this help and exits")
    info.add_argument('--usage', action='store_true', default=False,
                      help="Prints additional help on globs and exits")
    info.add_argument('--version', action='store_true', default=False,
                      help="Prints the version of formic and exits")
    info.add_argument('--license', action="store_true", help=SUPPRESS)
    return parser

def main(*kw):
    """Command line entry point; arguments must match those defined in
    in :meth:`create_parser()`; returns 0 for success, else 1.

    Example::

      command.main("-i", "**/*.py", "--no-default-excludes")

    Runs formic printing out all .py files in the current working directory
    and its children to ``sys.stdout``.

    If *kw* is None, :func:`main()` will use ``sys.argv``."""
    parser = create_parser()

    args = parser.parse_args(kw if kw else None)
    if args.help:
        parser.print_help()
    elif args.usage:
        print usage
    elif args.version:
        print "formic", get_version(), "http://www.aviser.asia/formic"
    elif args.license:
        print resource_string(__name__, "LICENSE.txt")
    else:
        try:
            fileset = FileSet(directory=args.directory,
                              include=args.include if args.include else ["*"],
                              exclude=args.exclude,
                              default_excludes=args.default_excludes,
                              symlinks=not args.no_symlinks)
        except FormicError as exception:
            parser.print_usage()
            print exception.message
            return 1

        prefix = fileset.get_directory()
        for directory, file_name in fileset.files():
            if args.relative:
                stdout.write(".")
            else:
                stdout.write(prefix)
            if dir:
                stdout.write(path.sep)
                stdout.write(directory)
            stdout.write(path.sep)
            stdout.write(file_name)
            stdout.write("\n")

    return 0

def entry_point():
    """Entry point for command line; calls :meth:`~formic.command.main()` and then
    :func:`sys.exit()` with the return value."""
    result = main()
    exit(result)

if __name__ == "__main__":
    main(*argv[1:])