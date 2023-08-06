#!/usr/bin/env python
#
# Closure Depresolver
# Copyright (C) 2012  Paul Horn
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
"""
Utility for Closure Library dependency calculation.

ClosureDepresolver scans source files for used and declared symbols.  From
this, the script produces calls for goog.provide and goog.require.

Paths to files can be expressed as individual arguments to the tool (intended
for use with find and xargs).  As a convenience, --root can be used to specify
all JS files below a directory.
"""
from __future__ import print_function


import argparse
import logging
import sys


from closure_depresolver import treescan, source



__author__ = 'knutwalker@gmail.com (Paul Horn)'

def _getArgparser():
    """Get the options parser."""

    parser = argparse.ArgumentParser(
        prog="closure-resolver",
        description=__doc__,
        version="%(prog)s 0.0.1",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '-n', '--namespace',
        dest='namespaces',
        action='append',
        required=True,
        default=[],
        help='One or more namespaces to scan dependencies for.  A namespaces '
             'is the top-level module of a Closure namespace.  The namespace '
             '`goog` will always be scanned.')

    parser.add_argument(
        '-i', '--input',
        dest='inputs',
        action='append',
        default=[],
        help='One or more input files to scan dependencies for.  If no files '
             'are given, the current working directory is recursivly '
             'traversed (implies --root=.)')

    parser.add_argument(
        'add_inputs',
        nargs='*',
        help='One or more input files to scan dependencies for.  If no files '
             'are given, the current working directory is recursivly '
             'traversed (implies --root=.)')

    parser.add_argument(
        '--root',
        dest='roots',
        action='append',
        default=[],
        help='The paths that should be traversed to scan the dependencies.'
             'If no files were given, the current working directory is '
             'recursivly  traversed (as in --root=.)')

    parser.add_argument(
        '--output_file',
        dest='output_file',
        action='store',
        help=('If specified, write output to this path instead of '
              'writing to standard output.'))

    return parser



def main(args=None):
    logging.basicConfig(format=(sys.argv[0] + ': %(message)s'),
                        level=logging.INFO)
    options = _getArgparser().parse_args(args)

    # Make our output pipe.
    if options.output_file:
        outfile = open(options.output_file, 'w')
        out = lambda *a, **k: print(*a, **(k.update(dict(file=outfile))))
    else:
        out = print

    # Scan current dir if nothing else was provided
    if not any((options.inputs, options.add_inputs, options.roots)):
        options.roots = ['.']

    input_namespaces = set(options.namespaces)

    sources = set()

    logging.info('Scanning paths...')
    for path in options.roots:
        for js_path in treescan.ScanTreeForJsFiles(path):
            sources.add(source.Source(js_path, input_namespaces))

    for js_path in set(options.inputs) | set(options.add_inputs):
        sources.add(source.Source(js_path, input_namespaces))

    logging.info('%s sources scanned.', len(sources))

    for js_source in sources:

        out(js_source.path)

        missing_requires = js_source.uses - js_source.requires
        superfluous_requires = js_source.requires - js_source.uses

        missing_provides = js_source.declares - js_source.provides
        superfluous_provides = js_source.provides - js_source.declares

        if any((missing_provides, missing_requires, superfluous_provides, superfluous_requires)):
            logging.info("Files are not balanced")

            if missing_provides:
                out("The following provides are missing")
                for m in missing_provides:
                    out("goog.provide('%s');" % m)

            if missing_requires:
                out("The following requires are missing")
                for m in missing_requires:
                    out("goog.require('%s');" % m)

            if superfluous_provides:
                out("The following provides are superfluous")
                for m in superfluous_provides:
                    out("goog.provide('%s');" % m)

            if superfluous_requires:
                out("The following requires are superfluous")
                for m in superfluous_requires:
                    out("goog.require('%s');" % m)

if __name__ == "__main__":
    main()