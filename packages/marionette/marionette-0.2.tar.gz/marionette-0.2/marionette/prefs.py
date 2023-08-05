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
from . import options

from json import dump as json_dump, load as json_load
from logging import getLogger
from os import makedirs
from os.path import join as path_join


__all__ = (
    'get_pref',
    'set_prefs',
)
logger = getLogger(__name__)


_prefs = None
def prefs():
    global _prefs
    prefs_path = path_join(options.pref_dir, 'prefs.json')
    if _prefs != None:
        return _prefs
    try:
        f = open(prefs_path)
    except IOError:
        _prefs = {}
        return _prefs
    try:
        _prefs = json_load(f)
    except ValueError:
        _prefs = {}
    return _prefs


def get_pref(name, default=None):
    return prefs().get(name, default)


def set_prefs(**kwargs):
    if not kwargs:
        return
    prefs()
    _prefs.update(kwargs)
    try:
        makedirs(options.pref_dir)
    except OSError:
        pass
    prefs_path = path_join(options.pref_dir, 'prefs.json')
    try:
        f = open(prefs_path, 'w')
    except OSError:
        logger.error('could not store prefs %s' % prefs_path)
    json_dump(_prefs, f, indent=4)
