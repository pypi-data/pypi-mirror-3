#!/usr/bin/env python
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
from ..prefs import get_pref, set_prefs
from ..worker import Worker

from optparse import OptionParser


def main():
    parser = OptionParser(usage='%prog cmd [cmd options]')
    options, args = parser.parse_args()

    # Make sure the worker has a key
    key = get_pref('cluster_key')
    if not key:
        key = input('Please enter a cluster key: ')
        set_prefs(cluster_key=key)

    # Run the worker
    worker = Worker(key)
    worker.work_forever()


if __name__ == '__main__':
    main()
