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
from json import load as json_load
from logging import DEBUG, Formatter, getLogger
from logging.handlers import RotatingFileHandler
from os.path import join as path_join, split as path_split


# This is the amount of kb we guarantee to log.
LOG_SIZE = 20


class Player(object):
    def __init__(self, name='player', directory=None, upgrades={}, level=1,
                 uid=None, api_version=None, new_git_url=None, img_url=None,
                 delete=False, settings=None):
        self.name = name
        self.set_directory(directory)
        self.upgrades = upgrades
        self.level = level
        self.uid = uid
        self.api_version = api_version
        self.new_git_url = new_git_url
        self.img_url = img_url
        self.delete = delete
        self.settings = settings
        self.units = {}
        self.logger = None

    def __str__(self):
        return self.name

    def set_directory(self, directory):
        self.directory = directory and directory.rstrip('/')
        if directory:
            self.sys_path, self.package_name = path_split(self.directory)

    def set_sys_path(self):
        import sys
        sys.path.append(self.sys_path)

    def import_package(self):
        return __import__(self.package_name)

    def unset_sys_path(self):
        import sys
        sys.path.remove(self.sys_path)

    def log(self, msg, lvl):
        if not self.directory:
            return
        if not self.logger:
            self.logger = getLogger(str(self.uid))
            self.logger.setLevel(DEBUG)
            log_path = path_join(self.directory, 'log.txt')
            rh = RotatingFileHandler(log_path, maxBytes=LOG_SIZE * 1000)
            fmt = '%(asctime)s %(levelname).8s: %(message)s'
            formatter = Formatter(fmt=fmt, datefmt='%y-%m-%d %H:%M:%S')
            rh.setFormatter(formatter)
            self.logger.addHandler(rh)
        getattr(self.logger, lvl)(msg)
