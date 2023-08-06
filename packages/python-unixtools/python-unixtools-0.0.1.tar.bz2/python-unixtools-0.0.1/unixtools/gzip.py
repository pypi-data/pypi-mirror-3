#!/usr/bin/env python
"""
unixtools.gzip - Unix gzip implemented in pure Python
"""
#
# Copyright 2008 by Hartmut Goebel <h.goebel@goebel-consult.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import absolute_import

__author__ = "Hartmut Goebel <h.goebel@goebel-cosnult.de>"
__copyright__ = "Copyright 2008 by Hartmut Goebel <h.goebel@goebel-consult.de>"
__licence__ = "GNU General Public License version 3 (GPL v3)"
__version__ = "0.0.1"

import gzip
import os
SUFFIX = '.gz'
BLOCKSIZE = 4096*10

def compress(filename, force=False, compresslevel=9):
    if not os.path.exists(filename):
        raise SystemExit('%s missing' % filename)
    if not (os.path.isfile(filename) or os.path.islink(filename)):
        raise SystemExit('not a file: %s' % filename)
    zfile = filename + SUFFIX
    if os.path.exists(zfile):
        if not force:
            raise SystemExit('%s already exists' % zfile)
        if os.path.islink(zfile):
            os.remove(zfile)
    zfh = gzip.open(zfile, 'wb', compresslevel=compresslevel)
    fh = open(filename, 'rb')
    while 1:
        data = fh.read(BLOCKSIZE)
        if not data:
            break
        zfh.write(data)
    fh.close()
    zfh.close()
    os.remove(filename)


def main():
    from optparse import OptionParser
    parser = OptionParser('%program [options] [ filename ... ]',
                          version=__version__)
    parser.add_option('-f', '--force', action='store_true')
    parser.add_option('-9', dest='compresslevel', 
                      action="store_const", const=9)

    opts, args = parser.parse_args()

    for fn in args:
        compress(fn, force=opts.force, compresslevel=opts.compresslevel)

if __name__ == '__main__':
    main()
