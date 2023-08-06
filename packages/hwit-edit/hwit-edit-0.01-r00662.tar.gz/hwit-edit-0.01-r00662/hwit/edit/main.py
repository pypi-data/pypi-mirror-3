#!/usr/bin/env python
#    -*-    encoding: UTF-8    -*-

#   copyright 2009 D Haynes
#
#   This file is part of the HWIT distribution.
#
#   HWIT is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   HWIT is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with HWIT.  If not, see <http://www.gnu.org/licenses/>.

__doc__ = """
`hwit.py` takes command line options to control its operation. By
default, it launches a graphical client window, but it may also be
operated in text mode.

To see what options are available, do::

    hwit.py -h

Currently, the following is fully implemented:
    *   Generate a form from an exported spreadsheet
    *   Launch the GUI client
    *   Launch the text console client
    *   Run unit tests

"""

import sys
from optparse import OptionParser
import logging
import warnings
import textwrap
from string import Template
import csv

import hwit.edit.app
from hwit.edit.doc.conf import release

USAGE = """
%prog is an application which comes with the Python HWIT library

Use it to manipulate HWIT files

examples:
    %prog                             launches GUI application
    %prog -c container.hwit           opens a text console
    %prog -g --tag=gp:fld < my_template.tsv
                                         generates a new HWIT form and
                                         creates a template tag in field
                                         'fld' of group 'gp'
""" 

def parser():
    rv = OptionParser(USAGE)
    rv.add_option("-v", "--verbose", action="store_true",
    default=False, help="increase the verbosity of log messages")
    rv.add_option("--version", action="store_true",
    default=False, help="print the version number of this program")
    return rv

def main(opts, args):

    if opts.version:       
        from hwit.edit.about import version_info
        sys.stdout.write(
        "HWIT editor %s-r%05d\n" %
        (release, int(version_info["revno"])))
        return 0

    if opts.verbose:
        logging.basicConfig(level=logging.DEBUG)
 
    return hwit.edit.app.main(opts, args)

def run():
    p = parser()
    opts, args = p.parse_args()
    rv = main(opts, args)
    sys.exit(rv)

if __name__ == "__main__":
    run()
