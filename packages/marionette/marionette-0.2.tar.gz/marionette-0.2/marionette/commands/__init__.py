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
from os import path as os_path
from pkgutil import iter_modules

all_commands = {}
_commands_dir = os_path.dirname(__file__)
_names = [cmd for _, cmd, _ in iter_modules([_commands_dir])]
_commands = __import__('marionette.commands', fromlist=_names)
for name in _names:
    all_commands[name] = getattr(_commands, name)
