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
from . import options
from .code import RemoteCode, SyncError
from .game import Game
from .http import ClusterClient, InvalidKeyError
from .sanitization import ParseError

from collections import defaultdict
from logging import getLogger
from random import randint, sample
from shutil import rmtree
from sys import exc_info, stderr
from tempfile import mkdtemp
from time import sleep
from traceback import format_tb
from urllib.error import URLError


__all__ = (
    'Worker',
)
logger = getLogger(__name__)


class Worker:
    def __init__(self, key):
        self.client = ClusterClient(options.domain, key, options.ssl)

    def fetch_players(self):
        if options.loud:
            print('Fetching players...')
        try:
            configs = self.client.fetch_players()
        except URLError:
            if options.loud:
                print('Trouble visiting ' + options.domain, file=stderr)
            return None

        logger.info('fetched %d players' % len(configs))

        # Parse the players
        flag_ids = []
        delete_ids = []
        good_players = []
        for config in configs:
            user_code = RemoteCode(config['uid'])
            user_code.set_server_config(config)
            try:
                user_code.sync()
                user_code.parse()
            except (ParseError, SyncError) as e:
                logger.info('user %d flagged: %s' % (config['uid'], str(e)))
                flag_ids.append(config['uid'])
                continue

            player = user_code.player()
            if player.delete:
                delete_ids.append(player.uid)
                continue

            good_players.append(player)

        # Delete some players
        if delete_ids:
            logger.info('deleting users: ' + ', '.join(map(str, delete_ids)))
            self.client.delete_players(delete_ids)

        # Flag some players
        if flag_ids:
            logger.info('flagging users: ' + ', '.join(map(str, flag_ids)))
            self.client.flag_players(flag_ids)

        # Sort and return
        good_players.sort(key=lambda player: player.level)
        return good_players

    def play_one_game(self, players, results, replay_dir):
        if options.loud:
            print('Running game...')

        # Create the game
        game = Game(900, 600, dirname=replay_dir, file_maxkb=512,
                    write_replay=bool(replay_dir))

        # Choose some players
        num_players = min(randint(2, 4), len(players))
        range_start = randint(0, max(0, len(players) - 10))
        population = players[range_start:range_start + 10]
        for player in sample(population, num_players):
            game.add_player(player)

        # Run the game
        try:
            game.run()
        except Exception as e:
            print(''.join(format_tb(exc_info()[2])), file=stderr, end='')
            print(str(type(e).__name__) + ': ' + str(e), file=stderr)
            return

        players_list = list(game.dead_players.values())
        for player in players_list:
            xp = 0
            for competitor in players_list:
                if player.final_round > competitor.final_round:
                    xp += competitor.level
            results[player.uid]['xp_awarded'] += xp
            results[player.uid]['games_played'] += 1
        if replay_dir:
            self.client.upload_replay(players_list, replay_dir)

    def fetch_and_run(self):
        # Fetch the players
        players = self.fetch_players()
        if players == None:
            return False
        logger.info('%d good players' % len(players))
        if len(players) < 2:
            if options.loud:
                print('Not enough players')
            return False

        # Run the games
        results = defaultdict(lambda: {
            'xp_awarded': 0,
            'games_played': 0,
        })
        for i in range(10):
            replay_dir = None
            if i % 10 == 0:
                replay_dir = mkdtemp()
            try:
                self.play_one_game(players, results, replay_dir)
            finally:
                if replay_dir:
                    rmtree(replay_dir)

        # Report the results
        player_lookup = dict([(p.uid, p) for p in players])
        results_list = []
        for player_id, result in results.items():
            result['player_id'] = player_id
            result['upgrades'] = player_lookup[player_id].upgrades
            result['name'] = player_lookup[player_id].name
            result['git_url'] = player_lookup[player_id].new_git_url
            result['img_url'] = player_lookup[player_id].img_url
            results_list.append(result)
        self.client.report_results(results_list)
        return True

    def work_forever(self):
        while True:
            try:
                success = self.fetch_and_run()
            except InvalidKeyError as e:
                print(e, file=stderr)
                return
            if not success:
                sleep(30)
