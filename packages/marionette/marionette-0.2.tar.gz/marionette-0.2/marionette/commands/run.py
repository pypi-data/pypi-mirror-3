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
# There was a young lady, precocious,
# Whose manners were simply atrocious.
#     When you inquire
#     Of her mis-matched attire,
# She'll tongue-lash you something ferocious!
#
from .. import options as moptions
from ..cmd_utils import fatality
from ..code import LocalCode, RemoteCode, SyncError
from ..game import Game
from ..replay.server import ReplayServer
from ..sanitization import ParseError

from optparse import OptionParser
from os.path import abspath, exists as path_exists, isdir
from shutil import rmtree
from sys import stderr
from tempfile import mkdtemp


def main():
    parser = OptionParser(usage='%prog cmd [cmd options]')
    parser.add_option('-f', '--nofetch', dest='fetch', default=True,
                      action='store_false', help='do not sync player code')
    parser.add_option('-k', '--noparse', dest='parse',
                      help='does not sanitize code in run',
                      default=True, action='store_false')
    parser.add_option('-n', '--noreplay', dest='write_replay',
                      help='runs the game without a replay',
                      default=True, action='store_false')
    parser.add_option('-o', '--overwrite', dest='overwrite',
                      help='overwrite replay directory',
                      default=False, action='store_true')
    parser.add_option('-r', '--replaydir', dest='replay_dir',
                      help='where to store the replay',
                      metavar='REPLAYDIR', default=None)
    parser.add_option('-v', '--noserve', dest='serve',
                      default=True, action='store_false',
                      help='do not run an HTTP server')
    options, args = parser.parse_args()
    if len(args) < 2:
        parser.error('Please supply at least two directories or ids')

    # Make a random replay_dir if one is not specified
    delete_replay_dir = not options.replay_dir
    options.replay_dir = options.replay_dir or mkdtemp()

    # Handle output directory conflicts
    if not options.write_replay:
        options.serve = False
    if (options.write_replay and not options.overwrite and
        path_exists(options.replay_dir) and not delete_replay_dir):
        overwrite = input('Overwrite %s [Y/n]? ' % options.replay_dir)
        if overwrite.lower() not in ('', 'y', 'yes'):
            return
        rmtree(options.replay_dir)

    # Create game
    game = Game(900, 600, options.replay_dir, options.write_replay,
                file_maxkb=64)

    # Create players from arguments
    for arg in args:
        if isdir(arg):  # directory
            user_code = LocalCode(abspath(arg))
        else:  # id
            try:
                uid = int(arg)
            except ValueError:
                parser.error('%s is not a directory or user id' % arg)
            user_code = RemoteCode(uid)

        # sync
        if options.fetch:
            with fatality(SyncError):
                user_code.sync()

        # parse
        if options.parse:
            with fatality(ParseError):
                warnings = user_code.parse()
            if moptions.loud:
                for warning in warnings:
                    print(warning, file=stderr)

        game.add_player(user_code.player())

    # Start the replay server
    if options.serve:
        server = ReplayServer(options.replay_dir)
        port = server.start()
        if moptions.loud:
            print('Serving at localhost:%d' % port)

    # Run the game
    try:
        try:
            result = game.run()
        except KeyboardInterrupt:
            game.kill()
            raise

        # Print the winners
        if len(game.winners) == 1:
            print(game.winners[0].name, 'wins!')
        else:
            print(', '.join(map(lambda p: p.name, game.winners)), 'tie!')

        # Continue serving indefinitely
        if options.serve:
            server.wait()
    except KeyboardInterrupt:
        if delete_replay_dir:
            rmtree(options.replay_dir)
        raise


if __name__ == '__main__':
    main()
