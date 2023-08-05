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
# While it may not be desirous
# (Even less so than Billy Cyrus),
#     We invite malicious code
#     To dwell within our abode.
# Good luck not catching a virus!
#
from . import options
from .http import UserClient
from .player import Player
from .sanitization import parse_dir, verify_settings

from json import load as json_load
from os import makedirs
from os.path import join as path_join, split as path_split
from re import search as re_search
from shutil import rmtree
from subprocess import PIPE, Popen
from urllib.error import URLError


__all__ = (
    'LocalCode',
    'RemoteCode',
    'SyncError',
)


class SyncError(Exception):
    pass


class UserCode:
    def __init__(self):
        self._player_config = None

    def parse(self):
        return parse_dir(self.directory)

    def player_config(self):
        if not self._player_config:
            settings_path = path_join(self.directory, 'settings.json')
            self._player_config = json_load(open(settings_path))
        return self._player_config

    def sync(self):
        return


class LocalCode(UserCode):
    def __init__(self, directory):
        super(LocalCode, self).__init__()
        self.directory = directory

    def player(self):
        return Player(
            name=self.player_config()['name'],
            directory=self.directory,
            upgrades=self.player_config().get('upgrades', {}),
            level=self.player_config()['level'],
            new_git_url=self.player_config().get('new_git_url'),
            delete=self.player_config().get('delete', False),
            uid=self.player_config().get('uid'),
            img_url=self.player_config().get('img_url', ''),
            settings=self.player_config(),
        )


class RemoteCode(UserCode):
    def __init__(self, uid):
        super(RemoteCode, self).__init__()
        self.uid = uid
        self._url = None
        self._server_config = None
        self._player_config = None
        self.client = UserClient(options.domain, options.ssl)

    @property
    def directory(self):
        return path_join(options.pref_dir, 'code', 'u%d' % self.uid)

    def set_server_config(self, config):
        self._server_config = config

    def server_config(self):
        if not self._server_config:
            self._server_config = self.client.get_config(self.uid)
        return self._server_config

    def url(self):
        if not self._url:
            self._url = self.server_config()['git_url']
        return self._url

    def current_url(self):
        try:
            p = Popen(['git', 'remote', 'show', '-n', 'origin'],
                      cwd=self.directory,
                      stdout=PIPE, stderr=PIPE)
        except OSError:
            return None
        if p.wait():
            return None
        for line in p.stdout:
            match = re_search(r'Fetch URL: (.*)', line.decode())
            if match:
                return match.group(1)
        return None

    def clone(self):
        try:
            rmtree(self.directory)
        except OSError:
            pass
        try:
            makedirs(path_split(self.directory)[0])
        except OSError:
            pass
        try:
            p = Popen(['git', 'clone', self.url(), self.directory],
                      stdout=PIPE, stderr=PIPE)
        except OSError:
            raise SyncError('`git clone %s` failed' % self.url())
        if p.wait():
            raise SyncError('`git clone %s` failed' % self.url())

    def pull(self):
        to_raise = False
        try:
            p = Popen(['git', 'pull'], cwd=self.directory,
                      stdout=PIPE, stderr=PIPE)
        except OSError:
            to_raise = True
        if to_raise or p.wait():
            raise SyncError('`git pull` failed')

    def sync(self, fail_quietly=False):
        net_down = False
        try:
            url = self.url()
        except URLError as e:
            msg = str(e)
            net_down = True
        if net_down and not fail_quietly:
            raise SyncError('Trouble retrieving git url (' + msg + ')')
        if net_down or self.current_url() == self.url:
            try:
                self.pull()
            except SyncError:
                if not fail_quietly:
                    raise
        else:
            self.clone()

    def parse(self):
        warnings = super(RemoteCode, self).parse()
        warnings.extend(verify_settings(self.server_config(),
                                        self.player_config()))
        return warnings

    def player(self):
        return Player(
            name=self.player_config()['name'],
            directory=self.directory,
            upgrades=self.player_config().get('upgrades', {}),
            level=self.server_config()['level'],
            new_git_url=self.player_config().get('new_git_url'),
            delete=self.player_config().get('delete', False),
            uid=self.server_config()['uid'],
            img_url=self.player_config().get('img_url', ''),
            settings=self.player_config()
        )
