#!/usr/bin/env python
"""
unixtools.tar - Unix tar implemented in pure Python
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

__author__ = "Hartmut Goebel <h.goebel@goebel-cosnult.de>"
__copyright__ = "Copyright 2008 by Hartmut Goebel <h.goebel@goebel-consult.de>"
__licence__ = "GNU General Public License version 3 (GPL v3)"
__version__ = "0.0.1"

import tarfile

def create(filename, filenames, recursive=1):
    tf = tarfile.TarFile.open(filename, 'w')
    for fn in filenames:
        arcname = fn.lstrip('/')
        tf.add(fn, arcname, recursive=recursive)
    tf.close()

def main():
    from optparse import OptionParser
    parser = OptionParser('%program [options] [ filename ... ]',
                          version=__version__)
    #parser.add_option('-A', '--catenate', '--concatenate',
    #                  help='append tar files to an archive')
    parser.add_option('-c', '--create', action='store_true',
                      help='create a new archive')
    #parser.add_option('-d', '--diff', '--compare', action='store_true',
    #                  help='find differences between archive and file system')
    #parser.add_option('--delete', action='store_true',
    #                  help='delete from the archive (not on mag tapes!')
    #parser.add_option('-r', '--append', action='store_true',
    #                  help='append files to the end of an archive')
    #parser.add_option('-t', '--list', action='store_true',
    #                  help='list the contents of an archive')
    #parser.add_option('--test-label', action='store_true',
    #                  help='test the archive volume label and exit')
    #parser.add_option('-u', '--update', action='store_true',
    #                  help='only append files newer than copy in archive')
    #parser.add_option('-x', '--extract', '--get', action='store_true',
    #                  help='extract files from an archive)
    parser.add_option('-f', '--file',
                      help='use archive file or device ARCHIVE')

    opts, args = parser.parse_args()
    if not opts.create:
        parser.error('option -c/--create is required (for now, sorry)')
    if not opts.file:
        parser.error('option -f/--file  is required (for now, sorry)')

    if opts.create:
        create(opts.file, args)

if __name__ == '__main__':
    main()
