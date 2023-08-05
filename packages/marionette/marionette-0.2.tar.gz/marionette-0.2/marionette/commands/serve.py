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
# Oversized glasses and 'stache
# Ironically carries no cash
#     Only liked Tool
#     Before they were cool
# And all of his plaid tends to clash.
#
from .. import options as moptions
from marionette.replay.server import ReplayServer


from optparse import OptionParser
from subprocess import Popen


def main():
    #Future: switch to argparser
    parser = OptionParser(usage='%prog cmd [cmd options]')
    options, args = parser.parse_args()
    if len(args) == 0:
        parser.error('You need to specify a directory to serve from.')
    directory = args[0]
    server = ReplayServer(directory)
    port = server.start()
    if moptions.loud:
        print('Serving at localhost:%d/' % port)
    server.wait()


if __name__ == '__main__':
    main()
