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
from collections import Callable
from marionette.player import Player
from marionette.units.unit import Unit
from os.path import join as path_join
from shutil import rmtree
from tempfile import mkdtemp
from time import sleep, time
from unittest import TestCase as BaseTestCase


__all__ = (
    'Test',
    'uses_temp_prefs',
)


def create_player_with_code(code, uid=1):
    p = Player(directory=mkdtemp(), uid=uid)
    f = open(path_join(p.directory, '__init__.py'), 'w')
    f.write('\n'.join(code) + '\n')
    f.close()
    return p


def create_sleeping_player(uid=1):
    return create_player_with_code([
        'import marionette.units',
        'import time',
        'class Toad(marionette.units.Unit):',
        '    def act(self):',
        '        time.sleep(3.0)',
        '        self.idle()',
    ], uid=uid)


def create_churning_player(uid=1):
    return create_player_with_code([
        'import marionette.units',
        'class Toad(marionette.units.Unit):',
        '    def act(self):',
        '        while True:',
        '            pass',
    ], uid=uid)


def create_churning_init_player(uid=1):
    return create_player_with_code([
        'import marionette.units',
        'class Toad(marionette.units.Unit):',
        '    def __init__(self):',
        '        while True:',
        '            pass',
    ], uid=uid)


def create_idling_player(uid=1):
    return create_player_with_code([
        'import marionette.units',
        'class Toad(marionette.units.Unit):',
        '    pass',
    ], uid=uid)


def delete_player_dir(p):
    rmtree(p.directory)


class Test(BaseTestCase):
    def pre_setup(self):
        self._created_players = []
        self._mocks = []

    def post_teardown(self):
        for player in self._created_players:
            delete_player_dir(player)
        for mock in reversed(self._mocks):
            if len(mock) == 3:
                setattr(*mock)
            else:
                delattr(*mock)

    def run(self, *args, **kwargs):
        self.pre_setup()
        super(Test, self).run(*args, **kwargs)
        self.post_teardown()

    def mock(self, obj, attr, value):
        if hasattr(obj, attr):
            self._mocks.append((obj, attr, getattr(obj, attr)))
        else:
            self._mocks.append((obj, attr))
        setattr(obj, attr, value)

    def mockf(self, obj, attr, value=None):
        margs = []
        def f(*args, **kwargs):
            margs.append((args, kwargs))
            if isinstance(value, Exception):
                raise value
            if isinstance(value, type) and issubclass(value, Exception):
                raise value('error!')
            return value
        self.mock(obj, attr, f)
        return margs

    def create_player_with_code(self, code, uid=1):
        player = create_player_with_code(code, uid=uid)
        self._created_players.append(player)
        return player

    def create_idling_player(self, uid=1):
        player = create_idling_player(uid=uid)
        self._created_players.append(player)
        return player

    def create_sleeping_player(self, uid=1):
        player = create_sleeping_player(uid=uid)
        self._created_players.append(player)
        return player

    def _wait(self, name, *args, timeout=2.0, interval=0.01, **kwargs):
        def do_assert():
            newargs = list(args)
            for i in range(len(newargs)):
                if isinstance(newargs[i], Callable):
                    newargs[i] = newargs[i]()
            getattr(self, name)(*newargs, **kwargs)
        start = time()
        while time() - start < timeout:
            try:
                do_assert()
                return
            except AssertionError:
                sleep(interval)
        do_assert()

    def assertWaitTrue(self, *args, **kwargs):
        self._wait('assertTrue', *args, **kwargs)

    def assertWaitFalse(self, *args, **kwargs):
        self._wait('assertFalse', *args, **kwargs)

    def assertWaitEquals(self, *args, **kwargs):
        self._wait('assertEquals', *args, **kwargs)

    def assertWaitGreater(self, *args, **kwargs):
        self._wait('assertGreater', *args, **kwargs)


def uses_temp_prefs(func):
    def new_test(self, *args, **kwargs):
        from . import options
        self.mock(options, 'pref_dir', mkdtemp())
        func(self, *args, **kwargs)
        try:
            rmtree(options.pref_dir)
        except OSError:
            pass
    return new_test


def uses_tempdir(func):
    def new_test(self, *args, **kwargs):
        self.tempdir = mkdtemp()
        func(self, *args, **kwargs)
        try:
            rmtree(self.tempdir)
        except OSError:
            pass
    return new_test
