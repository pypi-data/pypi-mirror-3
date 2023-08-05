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
# There once was a naive programmer
# Who maintained the most crippling stammer.
#     "If it's luh-lacking verbosity
#     it's a nuh-nail-like attrocity
# When juh-juh-juh-java is your hammer."
#
from .. import options
from ..sandbox import Sandbox
from ..units import isunittype, get_unit_property, get_unit_typenames
from ..version import version_is_valid, version_num, version_supported
from .parser import ParseError, parse

from hashlib import sha1
from imp import load_source
from json import loads as json_loads
from os import remove, walk
from os.path import (abspath, basename, exists as path_exists,
                     join as path_join, samefile, split as path_split)
from re import match as re_match


__all__ = (
    'parse_dir',
    'parse_file',
    'parse_license',
    'parse_py',
    'parse_settings',
    'verify_settings',
)


apache_sha1 = b'+\x8b\x81R)\xaa\x8aa\xe4\x83\xfbK\xa0X\x8b\x8blI\x18\x90'
def parse_license(text):
    warnings = []
    player_license = sha1(text.encode())
    if player_license.digest() != apache_sha1:
        raise ParseError('LICENSE file is invalid')
    return warnings


def parse_settings(text):
    warnings = []
    # Enforce size < 10kb
    if len(text) > 10000:
        raise ParseError('Your settings.json file is too large.  It must be '
                          'under 10k.')
    try:
        player_config = json_loads(text)
    except ValueError as e:
        raise ParseError('Invalid json (%s)' % str(e))

    # Ensure required attributes are defined
    for attribute in ('level', 'name', 'api_version'):
        if attribute not in player_config:
            raise ParseError('Missing "%s" attribute' % attribute)

    # level
    level = player_config['level']
    if not type(level) == int:
        raise ParseError('Value for "level" must be an int')

    # name
    name = player_config['name']
    if not type(name) == str:
        raise ParseError('Value for "name" must be a string')
    if not 0 < len(name) <= 100:
        raise ParseError('Name must be longer than 0 characters but '
                         'no longer than 100 characters')

    # api_version
    version = player_config['api_version']
    if type(version) != str:
        raise ParseError('Key "api_version" must be a string.')
    if not version_is_valid(version):
        raise ParseError('Key "api_version" must consist of integers '
                          'seperated by "."s.')
    if not version_supported(version):
        raise ParseError('Marionette is in version %s, and your api_version '
                         'is %s.  Your code may no longer run.  Please '
                         'update your code and your api_version.'
                         % (version_num, version))

    # upgrades
    upgrades = player_config.get('upgrades', {})
    if type(upgrades) != dict:  # upgrades
        raise ParseError('Upgrades must be a dictionary')
    total = 0
    for typename, unit_upgrades in upgrades.items(): # upgrades.unittype
        if not isunittype(typename):
            raise ParseError('"%s" is not a valid unit type' % typename)
        if level < get_unit_property(typename, 'min_user_level'):
            raise ParseError('You have upgrades for %s but you cannot use'
                             'that unit type until level %d' % (typename,
                             get_unit_property(typename, 'min_user_level')))
        if type(unit_upgrades) != dict:
            raise ParseError('Value for %s must be a dictionary' % typename)
        # upgrades.unittype.upgradetype
        for attribute, val in unit_upgrades.items():
            reference_upgrades = get_unit_property(typename, 'upgrades')
            if attribute not in reference_upgrades:
                raise ParseError('"%s" is not a valid upgrade type for %s.' %
                                 (attribute, typename))
            if (type(val) != int or val < 0 or
                val >= len(reference_upgrades[attribute])):
                raise ParseError('You cannot have upgrade level %s in %s '
                                 'for %s.' % (str(val), attribute, typename))
            total += val
    # check correct number of upgrades used
    max_upgrades = level - 1
    if total > max_upgrades:
        raise ParseError('%s has spent too many upgrades. (Only %d allowed.)' %
                         (name, max_upgrades))
        if total < level - 1 and options.loud:
            warnings.append('%s has %d more upgrades to spend!' %
                            (name, max_upgrades - total))
    # check all available unittypes used
    for typename in get_unit_typenames():
        if (level >= get_unit_property(typename, 'min_user_level') and typename
            not in upgrades):
            warnings.append('The unittype %s is available.  (To stop showing '
            'this notice, define upgrades for %s in your settings.json.)' %
            (typename, typename))

    # new_git_url
    new_git_url = player_config.get('new_git_url')
    if new_git_url and not re_match('(git|https?)://'):
        raise ParseError(
                'new_git_url must start with git://, http://, or https://')

    return warnings


def parse_py(text):
    warnings = []
    parse(text)
    return warnings


def parse_file(filename):
    # Make sure this is a file we want to parse
    base_filename = basename(filename)
    if (base_filename not in ('LICENSE', 'settings.json') and
        not base_filename.endswith('.py')):
        return []

    # Make sure we can read the file
    try:
        file_contents = open(filename).read()
    except UnicodeDecodeError:
        raise ParseError('%s could not be opened.' % filename)

    # Handle individual file types
    warnings = []
    try:
        if base_filename == 'LICENSE':  # LICENSE
            warnings.extend(parse_license(file_contents))
        elif base_filename == 'settings.json':  # settings.json
            warnings.extend(parse_settings(file_contents))
        elif base_filename.endswith('.py'):  # *.py
            warnings.extend(parse_py(file_contents))
    except ParseError as e:
        raise ParseError('%s [%s]' % (str(e), filename))
    for i, warning in enumerate(warnings):
        warnings[i] = '%s [%s]' % (warning, filename)
    return warnings


def parse_dir(directory):
    """Make sure a players code directory is OK.

    This is a destructive function in that we remove .pyc files

    """
    warnings = []

    # Check for a valid license and settings file in root directory
    for name in ('LICENSE', 'settings.json', '__init__.py'):
        if not path_exists(path_join(directory, name)):
            raise ParseError('No %s file in root directory [%s]' %
                             (name, directory))

    # Parse all files, and collect a list of all .py files
    py_files = []
    for dirpath, _, filenames in walk(directory):
        for filename in filenames:
            full_path = path_join(dirpath, filename)
            if (filename == 'settings.json' and
                    not samefile(dirpath, directory)):
                continue
            if filename.endswith('.pyc'):
                remove(full_path)
                continue
            if filename.endswith('.py'):
                py_files.append(full_path)
            warnings += parse_file(full_path)

    # This is so the user can't write anything damaging to the modules
    import sys
    # Append ..directory to path, and try to load each .py file.
    # (We append so the user's code is considered a "package", and the user
    # can do relative imports.)
    syspath_name, module_name = path_split(abspath(directory).rstrip('/'))
    sys.path.append(syspath_name)
    sandbox = Sandbox()
    with sandbox.context():
        try:
            __import__(module_name)
        except Exception as e:
            raise ParseError('%s could not be imported (%s)' %
                             (module_name, str(e)))
    sys.path.pop()
    return warnings


def verify_settings(server_config, player_config):
    warnings = []

    # level
    player_level = player_config['level']
    server_level = server_config['level']
    if player_level > server_level:
        raise ParseError('Level too high for %s!  (Real level is %d.)' %
                          (player_config['name'], server_level))
    if player_level < server_level:
        warnings.append('Level too low for %s!  (Real level is %d.)' %
                        (player_config['name'], server_level))

    # uid
    if not 'uid' in player_config:
        warnings.append("%s doesn't specify uid in their settings.json.  "
                        'While not required, we recommend having one.' %
                        player_config['name'])
    else:
        if player_config['uid'] != server_config['uid']:
            raise ParseError("uid does not match for %s." %
                              player_config['name'])

    return warnings
