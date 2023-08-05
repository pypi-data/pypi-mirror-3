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
from imp import find_module
from os.path import join as path_join
from re import compile as re_compile


_marionette_dir = find_module('marionette')[1]
_defs_dir = path_join(_marionette_dir, 'sanitization', 'defs')
def _get_names(listname):
    for line in open(path_join(_defs_dir, listname + '.txt')):
        line = line.strip()
        if line and line[0] != '#':
            yield line


kw_blacklist = set(_get_names('kw_blacklist'))
kw_graylist = set(_get_names('kw_graylist'))
mod_whitelist = set(_get_names('mod_whitelist'))


_rel_re = re_compile('\.*')
def subattrs(attr):
    index = len(_rel_re.match(attr).group(0))
    if index != 0 and index != len(attr):
        yield attr[:index]
    index = attr.find('.', index)
    while index != -1:
        yield attr[:index]
        index = attr.find('.', index + 1)
    yield attr


def prefixes(colorlist):
    for attr in colorlist:
        for subattr in subattrs(attr):
            yield subattr


mod_whitelist_prefixes = set(prefixes(mod_whitelist))


def attr_in_colorlist(attr, colorlist):
    for subattr in subattrs(attr):
        if subattr in colorlist:
            return True
    return False
