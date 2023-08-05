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
from ..prefs import set_prefs


from json import dump as json_dump, dumps as json_dumps, load as json_load
from optparse import OptionParser
from os.path import exists as path_exists, expanduser, join as path_join


def main():
    parser = OptionParser(usage='%prog cmd [cmd options]')
    options, args = parser.parse_args()
    if len(args) == 0:
        parser.error('Please provide at least one setting and value.')

    change_dict = {}
    for arg in args:
        arg = arg.split('=')
        if len(arg) != 2:
            parser.error('Settings should be of the form "name=value".')
        change_dict[arg[0]] = arg[1]
    set_prefs(**change_dict)


if __name__ == '__main__':
    main()
