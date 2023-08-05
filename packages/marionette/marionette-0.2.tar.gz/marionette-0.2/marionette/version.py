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
# These aren't cute like Ubuntu;
# And that is a true grunt too.
#     An adjectived critter
#     Will make you twitter
# Whether or not you want to.
#
from . import options
from .prefs import get_pref, set_prefs

from time import time
from urllib.error import URLError


__all__ = (
    'check_update',
    'version_num',
)


version_num = '0.2'


def check_update():
    """Check current version of game (if allowed)"""
    permission = get_pref('allow_update_check')
    new_prefs = {}

    if permission == None:
        answer = input('Allow marionette to check for updates [y/N]? ')
        permission = answer.lower() in ('y', 'yes')
        new_prefs['allow_update_check'] = permission

    passed_time = time() - get_pref('last_update_check', 0)
    if permission and passed_time > 24 * 60 * 60:
        from .http import UserClient
        client = UserClient(options.domain, options.ssl)
        try:
            min_version = client.get_min_user_version()
        except URLError:
            return
        new_prefs['last_update_check'] = time()
        if version_lt(version_num, min_version):
            print('Your current version is no longer compatable, please '
                  'download the newest version from mutantmarionette.com.')

    set_prefs(**new_prefs)


def version_is_valid(version):
    return not any(map(lambda x: not x.isdigit(), version.split('.')))


def version_supported(player_version):
    return player_version == version_num


def version_lt(v1, v2):
    num = lambda v: tuple(map(int, v.split('.')))
    return num(v1) < num(v2)
