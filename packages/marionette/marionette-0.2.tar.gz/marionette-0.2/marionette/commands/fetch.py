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
# There once was a girl, Mabel Jean,
# Who hated all food but string beans.
#     Raw, baked, or fried,
#     Ate them pickled, or dried,
# Till all of her skin had turned green!
#
from ..cmd_utils import fatality
from ..code import SyncError, RemoteCode

from optparse import OptionParser


__all__ = (
    'main',
)


def main():
    parser = OptionParser(usage='%prog cmd [cmd options]')
    options, args = parser.parse_args()
    for arg in args:
        try:
            uid = int(arg)
        except ValueError:
            parser.error('Argument "%s" is not a user id' % arg)
        with fatality(SyncError):
            RemoteCode(uid).sync()


if __name__ == '__main__':
    main()
