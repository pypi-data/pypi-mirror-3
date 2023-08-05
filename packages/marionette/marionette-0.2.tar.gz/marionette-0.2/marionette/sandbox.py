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
from contextlib import contextmanager
from imp import find_module, load_dynamic, load_source
from io import StringIO


__all__ = (
    'Sandbox',
)


class Sandbox:
    def __init__(self):
        # We can never really be without the os module, so go ahead and create
        # a dirty version of it
        filename = find_module('os')[1]
        dirty_os = load_source('_dirty_os', filename)
        dirty_os.__name__ = 'os'

        # sys.stderr doesn't come back with a secondary import of sys.
        # We need to make sure we have one
        dirty_sys = load_dynamic('___sys', 'sys')
        dirty_os.__name__ = 'sys'
        dirty_sys.stderr = StringIO()

        self._dirty_modules = {
            'os': dirty_os,
            'os.path': dirty_os.path,
            'sys': dirty_sys,
        }

    @contextmanager
    def context(self):
        import sys
        clean_modules = dict(sys.modules)
        sys.modules.clear()
        sys.modules.update(self._dirty_modules)
        try:
            yield
        finally:
            self._dirty_modules = dict(sys.modules)
            sys.modules.clear()
            sys.modules.update(clean_modules)
