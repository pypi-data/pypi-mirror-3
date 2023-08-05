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
from json import dumps as json_dumps
from os import makedirs
from os.path import join as path_join, exists as path_exists


class Replay(object):
    def __init__(self, directory, file_maxkb=64, write=True):
        """file_maxkb measured in kb"""
        self.directory = directory
        self.file_maxkb = file_maxkb
        self.write = write
        if self.write:
            try:
                makedirs(directory)
            except OSError:
                pass
        self.round_list = '['
        self.fnumber = 0

    def write_round(self, around):
        if len(self.round_list) > 1:
            self.round_list += ', '
        self.round_list += json_dumps(dict(around))
        if len(self.round_list) >= self.file_maxkb * 1024:
            self.dump()


    def dump(self):
        if not self.write:
            return
        self.round_list += ']'
        f = open(path_join(self.directory, str(self.fnumber)), 'w')
        f.write(self.round_list)
        f.close()
        self.fnumber += 1
        self.round_list = '['
