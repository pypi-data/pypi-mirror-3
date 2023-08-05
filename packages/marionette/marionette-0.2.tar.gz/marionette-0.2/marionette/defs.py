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
from json import load as json_load
from os import listdir
from os.path import join as path_join


__all__ = (
    'create_base_data',
    'create_defs',
)


_marionette_dir = find_module('marionette')[1]
def create_defs(submodule, datadir='defs'):
    args = submodule.split('.')
    args.append(datadir)
    directory = path_join(_marionette_dir, *args)
    defs = {}
    for filename in listdir(directory):
        if filename == 'base.json' or not filename.endswith('.json'):
            continue
        data = json_load(open(path_join(directory, filename)))
        defs[data['typename']] = data
    return defs


def create_base_data(submodule, datadir='defs'):
    args = submodule.split('.')
    args.append(datadir)
    args.append('base.json')
    return json_load(open(path_join(_marionette_dir, *args)))
