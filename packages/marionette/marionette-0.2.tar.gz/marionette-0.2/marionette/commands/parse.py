#!/usr/bin/env python
#
#   Copyright 2011 Inkylabs et al.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# <Insert Marionetastical limerick here>
#
from ..cmd_utils import fatality
from ..code import LocalCode, RemoteCode, SyncError
from ..sanitization import ParseError, parse_file

from os.path import isdir, isfile
from optparse import OptionParser
from sys import stderr, stdin


__all__ = (
    'main',
)


def main():
    #Future: switch to argparser
    parser = OptionParser(usage='%prog file ...')
    parser.add_option('-f', '--nofetch', dest='fetch', default=True,
                      action='store_false', help='do not sync player code')
    options, args = parser.parse_args()

    # If we are just piping data, parse it all as one file
    if not stdin.isatty():
        with fatality(ParseError):
            parse(stdin.read())
        return

    # Verify arguments
    if len(args) == 0:
        parser.error('You need at least one file or directory.')

    # Handle each argument
    for arg in args:
        if isfile(arg):  #file
            with fatality(ParseError):
                warnings = parse_file(arg)
        else:
            if isdir(arg):  # directory
                user_code = LocalCode(arg)
            else:  # id
                try:
                    uid = int(arg)
                except ValueError:
                    parser.error('Argument must be a directory, filename, '
                                 'or user id')
                user_code = RemoteCode(uid)
            if options.fetch:
                with fatality(SyncError):
                    user_code.sync()
            with fatality(ParseError):
                warnings = user_code.parse()
        for warning in warnings:
            print(warning, file=stderr)


if __name__ == '__main__':
    main()
