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
from ..items import get_item_property
from ..player import Player
from ..sandbox import Sandbox
from .defs import get_unit_properties, get_unit_property
from .unit import (ParamError, Unit, copy_values, decoded_pos,
                   initialize_values, resolve_attributes, verify_action)

from logging import getLogger
from multiprocessing import Manager, Pipe, Process
from multiprocessing.managers import RemoteError
from os import getpid, kill as pkill
from signal import SIGCONT, SIGKILL, SIGSTOP
from socket import error as socket_error
from sys import exc_info
from threading import Event, Lock, Semaphore, Thread
from time import sleep, time
from traceback import format_tb
from types import MethodType


# Future python 3.3 - see if we can remove this
# This is a hack to deal with some nasty python race conditions
# http://stackoverflow.com/questions/1359795
# http://bugs.python.org/issue1731717
from signal import SIGCLD, SIG_DFL, signal
signal(SIGCLD, SIG_DFL)


__all__ = (
    'SandboxedUnit',
    'SandboxedUnitFactory',
    'SandboxedUnitProcess',
)
logger = getLogger(__name__)


def to_camel_case(typename):
    do_caps = True
    ret = ''
    for c in typename:
        if c == '_':
            do_caps = True
            continue
        if do_caps:
            ret += c.upper()
            do_caps = False
            continue
        ret += c
    return ret


def sandboxed(func):
    def new_func(self, *args, **kwargs):
        with self._sandbox.context():
            return func(self, *args, **kwargs)
    return new_func


class SandboxedUnitProcess(Process):

    """The sandboxed unit process that runs and monitors the client code.

    Things that must be verified before running this:
    * The file exists
    * The code passes the sanitization test

    This code is partitioned into methods that run in the parent process, and
    methods that run in the child process.

    """

    # BEGIN PARENT METHODS

    def __init__(self, typename, player, origin=(0, 0), uid=0, manager=None,
                 semaphore=None, speed_factor=1.0):
        # Setup the process
        super(SandboxedUnitProcess, self).__init__()
        self.daemon = True

        # Base variables
        self._sandbox = Sandbox()
        self.player = player
        self.origin = origin
        self.uid = uid
        for key, value in get_unit_properties(typename):
            setattr(self, key, value)
        self._start_memory = 0

        # Create shared variables
        self._unit_data = manager.dict()
        default_action_data = get_unit_property(typename, 'default_action_data')
        self._action_data = manager.list([default_action_data])
        self._err_data = manager.list()
        self._log_data = manager.list()
        self._parent_pipe, self._child_pipe = Pipe()

        # Fun threading things
        self._started = Event()
        self._lock = Lock()
        self._semaphore = semaphore or Semaphore()
        self.ready = True

        # Set default attribute values
        upgrades = player.upgrades.get(typename, {})
        self._values = resolve_attributes(self.typename, upgrades)
        initialize_values(self.__dict__, self._values)
        self.max_time = self.max_time / speed_factor
        copy_values(self.__dict__, self._unit_data, self._values)

    def __str__(self):
        return self.typename + ':' + str(self.uid)

    def send_signal(self, sig):
        self._started.wait()
        try:
            pkill(self.pid, sig)
        except OSError as e:
            pass

    def kill(self):
        self.send_signal(SIGKILL)
        self.join(.5)

    def suspend(self):
        self.send_signal(SIGSTOP)

    def resume(self):
        self.send_signal(SIGCONT)

    def getmem(self):
        """Get the number of bytes in vmem for the sandboxed process"""
        filename = '/proc/%d/stat' % (self.pid or getpid())
        try:
            data = open(filename).read()
        except IOError:
            return 0
        return int(data.split()[22])

    def _do(self, cmd, args=[], kwargs={}):
        # If the player isn't ready, the just skip this command and keep
        # churning on their previous one
        if self.ready:
            self._parent_pipe.send([cmd, args, kwargs])
        self.ready = self._parent_pipe.poll(self.max_time)
        errors = []
        ret = {}
        if self.ready:
            ret = self._parent_pipe.recv()
        else:
            errors.append('TimeError: Used more than %fs' % self.max_time)

        if self.getmem() - self._start_memory > self.max_memory * 1024:
            errors.append('MemoryError: Used more than %fK of memory' %
                          self.max_memory)
            self.kill()
        elif ret.get('fatal', False):
            self.kill()
        else:
            self.suspend()

        # Log errors and requested logs
        try:
            errors.extend(self._err_data)
            for err in errors:
                self.player.log(err, 'error')
            del self._err_data[:]
            for msg, lvl in self._log_data:
                self.player.log(msg, lvl)
            del self._log_data[:]
        except (EOFError, IOError, RemoteError):
            logger.warn('Logging failed')

    def _lock_do(self, cmd, args=[], kwargs={}, queue=None, resume=True,
            acquire=True):
        # Acquire locks and start the process
        if acquire:
            self._lock.acquire()
        self._semaphore.acquire()
        if resume:
            self.resume()

        # Only run if the process is alive
        if self.is_alive():
            self._do(cmd, args=args, kwargs=kwargs)

        # Add this unit to a queue if we need to
        if queue:
            queue.put(self)

        # Release locks
        self._semaphore.release()
        self._lock.release()

    def _work(self, name, queue=None):
        Thread(target=getattr(self, '_%s_work' % name),
               kwargs={'queue': queue}).start()

    def _start_work(self, queue=None):
        try:
            # It's possible that a sibling process dies right as
            # super.start gets called
            # http://bugs.python.org/issue1731717
            while True:
                try:
                    super(SandboxedUnitProcess, self).start()
                except OSError:
                    pass
                else:
                    break

            # Since we have spawned the child, we don't need the child pipe.
            # It maintains a file handle, so keeping this around would put
            # us in greater danger of reaching the maximum file handle limit.
            del self._child_pipe

            self._start_memory = self._parent_pipe.recv()
            self._started.set()
            self._lock_do('start', queue=queue, resume=False, acquire=False)
        except KeyboardInterrupt:
            pass

    def _act_work(self, queue=None):
        try:
            copy_values(self.__dict__, self._unit_data, self._values)
            self._lock_do('act', queue=queue)
        except KeyboardInterrupt:
            pass

    def start(self, queue=None):
        self._lock.acquire()
        self._work('start', queue)

    def act(self, queue=None):
        self._work('act', queue)

    @property
    def action_data(self):
        try:
            return self._action_data[0]
        except IOError:
            logger.warn('Returning action data failed')
        return get_unit_property(self.typename, 'default_action_data')

    # END PARENT METHODS

    @sandboxed
    def _start(self):
        self.unit = Unit()
        mod = self.player.import_package()
        cameled = to_camel_case(self.typename)
        unit_class = getattr(mod, cameled, None)
        import marionette.units
        if (not isinstance(unit_class, type) or
            not issubclass(unit_class, marionette.units.Unit)):
            raise ImportError('Cannot import %s' % cameled)
        init = unit_class.__init__
        # We swap out the users init and do something important things before
        # putting it back and actually calling it.
        unit_class.__init__ = lambda s: None
        if not hasattr(unit_class, 'used_time'):
            unit_class.used_time = \
                property(lambda s: time() - self._start_time)
        if not hasattr(unit_class, 'used_memory'):
            unit_class.used_memory = \
                property(lambda s: self.getmem() - self._start_memory)
        self.unit = unit_class()
        self.unit.uid = self.uid
        self.unit.player = self.player.uid
        copy_values(self._unit_data, self.unit.__dict__, self._values)
        self.unit.__init__ = MethodType(init, self.unit)
        self.unit.__init__()

    @sandboxed
    def _act(self):
        copy_values(self._unit_data, self.unit.__dict__, self._values)
        action_data = self.unit.act()
        # Verify action
        try:
            verify_action(action_data, self.typename)
        except ParamError as e:
            self._err_data.append(str(e))
            return
        if self.unit.rounds_committed != None:
            return
        if 'pos' in action_data[1]:
            newpos = decoded_pos(action_data[1]['pos'], self.origin)
            action_data[1]['pos'] = newpos
        self._action_data[0] = action_data

    def handle_parent_command(self):
        cmd, args, kwargs = self._child_pipe.recv()
        self._start_time = time()
        try:
            response = getattr(self, '_' + cmd)(*args, **kwargs) or {}
        except Exception as e:
            response = {}
            tb = ''.join(format_tb(exc_info()[2]))
            try:
                self._err_data.append(tb + type(e).__name__ + ': ' + str(e))
            except socket_error:
                logger.warn('Error adding error')
        self._child_pipe.send(response)

    def run(self):
        try:
            # Prepare sys.path for importing the players package
            syspath_name = self.player.set_sys_path()

            with self._sandbox.context():
                # Import some packages that the process will probably need
                import marionette.items
                import marionette.logging
                import marionette.settings
                import marionette.units
                import marionette.utils.spatial

                # Some values in these modules need to be specific for the
                # player
                marionette.logging._log_data = self._log_data
                marionette.settings._settings = self.player.settings
                marionette.settings._properties = {}
                for typename, upgrades in self.player.upgrades.items():
                    properties = resolve_attributes(typename, upgrades)
                    marionette.settings._properties[typename] = properties

            self._start_memory = self.getmem()
            self._child_pipe.send(self._start_memory)
            while True:
                self.handle_parent_command()
        except KeyboardInterrupt:
            pass


def read_cpu_speeds():
    ret = []
    for line in open('/proc/cpuinfo'):
        if line.startswith('cpu MHz'):
            ret.append(float(line.split(': ')[1]))
    return ret


def approx_cpu_speed():
    _allmhz = []
    for i in range(4):
        _allmhz += read_cpu_speeds()
        sleep(.05)
    return min(_allmhz) / 1000


class SandboxedUnitFactory(object):
    def __init__(self, cpus=len(read_cpu_speeds()),
                 speed_factor=approx_cpu_speed()):
        self.semaphore = Semaphore(cpus)
        self.speed_factor = speed_factor
        # Creating the manager is not as fault tolerant as we would like
        while True:
            try:
                self.manager = Manager()
            except OSError:
                sleep(.1)
            else:
                break

    def SandboxedUnit(self, *args, **kwargs):
        defaults = {
            'manager': self.manager,
            'semaphore': self.semaphore,
            'speed_factor': self.speed_factor
        }
        defaults.update(kwargs)
        unit = SandboxedUnitProcess(*args, **defaults)
        unit.start()
        return unit


_default_factory = None
def SandboxedUnit(*args, **kwargs):
    global _default_factory
    if _default_factory == None:
        _default_factory = SandboxedUnitFactory()
    return _default_factory.SandboxedUnit(*args, **kwargs)
