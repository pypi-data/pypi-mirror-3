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
from .items import Item, get_item_property
from .player import Player
from .replay import Replay, Round
from .units import SandboxedUnit, get_unit_property
from .utils.spatial import overlaps
from .world import World

from logging import getLogger
from math import ceil, sqrt
from queue import Queue
from random import randint

__all__ = (
    'Game',
    'time_per_round'
)
logger = getLogger(__name__)
time_per_round = 0.1


class IDManager(set):
    def generate(self, uid=None):
        if uid == None or uid in self:
            uid = randint(0, 1<<31)
            while uid in self:
                uid = randint(0, 1<<31)
        self.add(uid)
        return uid


class Game(object):
    def __init__(self, width, height, dirname='replay', write_replay=True,
                 file_maxkb=64):
        self.uids = IDManager()
        self.world = World(width, height, self.uids)
        self.replay = Replay(dirname, file_maxkb = file_maxkb,
                             write=write_replay)
        self.dirname = dirname
        self.max_time = 3000
        self.curround = Round()
        self.world.curround = self.curround
        self.round_num = 0
        self.dead_players = {}
        self.distance_dict = {}
        self.players = {}
        self.winners = []


    def populate_winners(self):
        max_round = max(map(lambda p: p.final_round,
                            self.dead_players.values()))
        self.winners = [p for p in self.dead_players.values()
                        if p.final_round == max_round]


    def run(self):
        """Returns a dictionary mapping player ids to the round they died."""
        self.curround['dimensions'] = (self.world.width, self.world.height)
        for i in range(0, 10):
            self.world.make_item('grutonium')
        for player in self.players.values():
            for i in range(0,3):
                self.add_unit('toad', player)
            self.curround.change(player.uid, {
                'type': 'Player',
                'name': player.name,
            })
        self.replay.write_round(self.curround)

        while self.run_round():
            pass

        self.replay.dump()
        self.populate_winners()


    def run_round(self):
        logger.debug('________Round ' + str(self.round_num) + '________')

        self.curround = Round()
        self.world.curround = self.curround
        queue = Queue()
        for unit in self.world.units.values():
            self.give_data(unit)
            unit.act(queue=queue)

        # Handle each units actions
        for i in range(len(self.world.units)):
            unit = queue.get()
            if not unit.is_alive():
                self.unit_die(unit)
                continue
            cmd, params = unit.action_data
            getattr(self, 'unit_' + cmd)(unit, **params)
            unit.rounds_committed = unit.rounds_committed or None
            if unit.rounds_committed != None:
                unit.rounds_committed -= 1
                self.curround.change(unit.uid, {
                    'committed': unit.rounds_committed
                })
        ret = self.inc()

        self.replay.write_round(self.curround)

        return ret

    def give_data(self, unit):
        # Populate units_in_view
        del unit.units_in_view[:]
        for other in self.world.units.values():
            if (unit != other and
                self.world.distance(unit, other) <= unit.range_of_sight):
                unit.units_in_view.append(other)

        # Populate items_in_view
        del unit.items_in_view[:]
        for item in self.world.items.values():
            if self.world.distance(unit, item) <= unit.range_of_sight:
                unit.items_in_view.append(item)

        # Populate obstacles_in_view
        del unit.obstacles_in_view[:]
        for obstacle in self.world.cd.objects:
            if self.world.distance(unit, obstacle) <= unit.range_of_sight:
                unit.obstacles_in_view.append(obstacle)

    def add_player(self, player):
        player.uid = self.uids.generate(player.uid)
        self.players[player.uid] = player

    def add_unit(self, typename, player, pos=None):
        uid = self.uids.generate()
        unit = SandboxedUnit(typename, player, self.world.orig, uid)
        unit.pos = pos or self.world.place_random(unit.size)
        player.units[uid] = unit
        self.world.units[uid] = unit
        self.curround.change(unit.uid, {
            'type': unit.typename,
            'player': unit.player.uid,
            'pos': unit.pos,
            'maxHealth': unit.max_health,
            'health': unit.health,
            'intent': 'idle',
        })
        logger.debug(player.name + ' made a ' + typename)

    def scatter_inventory(self, unit):
        for itemtype in unit.inventory:
            uid = self.uids.generate()
            size = get_item_property(itemtype, 'size')
            pos = self.world.randomize_pos(unit.pos, size, 20)
            self.world.make_item(itemtype, unit.inventory[itemtype], pos)

    def modify_inventory(self, unit, typename, delta):
        unit.inventory.setdefault(typename, 0)
        unit.inventory[typename] += delta
        if unit.inventory[typename] == 0:
            del unit.inventory[typename]
        weight = delta * get_item_property(typename, 'weight_per_unit')
        unit.inventory_weight += delta

    def player_die(self, player):
        player.final_round = self.round_num
        self.dead_players[player.uid] = player
        self.curround.change(player.uid, {'end': True})
        logger.debug(player.name + ' died')
        del self.players[player.uid]

    def unit_attack(self, unit, uid):
        if uid not in self.world.units:
            return None
        target = self.world.units[uid]
        # unit is waiting to attack
        if unit.rounds_committed:
            logger.debug('%d rounds until attack' % unit.rounds_committed)
            return
        # unit has just started to attack
        if unit.rounds_committed == None:
            unit.rounds_committed = int(ceil(unit.attack_time_req /
                                        float(time_per_round)))
            logger.debug('Unit %d is attacking' % unit.uid)
            direction = self.world.calc_direction(target.pos[0] - unit.pos[0],
                    target.pos[1] - unit.pos[1]) or 'S'
            self.curround.change(unit.uid, {
                'intent': 'attack' + direction,
            })
            return
        # unit is finished waiting to attack
        if not overlaps(unit, target):
            return
        target.health -= unit.melee_strength
        self.curround.change(target.uid, {'health': max(target.health, 0)})
        logger.debug('Unit %d damaged unit %d %d points' %
                                (unit.uid, target.uid, unit.melee_strength))

    def unit_die(self, unit):
        self.curround.change(unit.uid, {'end': True, 'intent': 'die'})
        self.world.units.pop(unit.uid)
        unit.player.units.pop(unit.uid)
        if len(unit.player.units) == 0:
            self.player_die(unit.player)
        unit.kill()
        # TODO: when randomize_pos todo is fixed, scatter from center
        if hasattr(unit, 'inventory'):
            self.scatter_inventory(unit)

    def unit_drop(self, unit, typename, amount):
        if typename not in unit.inventory:
            unit.player.log("You tried to drop an item not in your inventory."
                            % unit.player, 'warning')
            return
        amount = min(unit.inventory[typename], amount)
        self.modify_inventory(unit, typename, -amount)
        self.curround.change(unit.uid, {
            'inventory': unit.inventory,
        })
        item = Item(typename, unit.pos, amount, self.uids.generate())
        self.world.items[item.uid] = item
        self.curround.change(item.uid, {
            'amount': item.amount,
            'intent': 'drop',
            'pos': item.pos,
            'type': typename,
        })
        logger.debug('Unit %d dropped %d %s' % (unit.uid, amount,
                typename))

    def unit_eat(self, unit, typename, amount):
        amount = min(amount, unit.inventory.get(typename, 0))
        self.modify_inventory(unit, typename, -amount)
        effects = unit.metabolism[typename]
        change_dict = {}
        for attr, change in effects.items():
            val = getattr(unit, attr) + change * amount
            val = min(val, getattr(unit, 'max_' + attr))
            setattr(unit, attr, val)
            change_dict[attr] = getattr(unit, attr)
        change_dict.update({'inventory': unit.inventory, 'intent': 'eat'})
        self.curround.change(unit.uid, change_dict)
        logger.debug('Unit %d ate %d %s' % (unit.uid, amount, typename))

    def unit_grab(self, unit, uid, amount):
        item = self.world.items.get(uid)
        if item == None or not overlaps(unit, item):
            return
        capacity = int((unit.max_inventory_weight - unit.inventory_weight) /
                       item.weight_per_unit)
        amount = min(amount, item.amount, capacity)
        self.modify_inventory(unit, item.typename, amount)
        item.amount -= amount
        if item.amount == 0:
            self.curround.change(uid, {'end': True, 'intent': 'die'})
            del self.world.items[uid]
        self.curround.change(unit.uid, {
            'intent': 'grab',
            'inventory': unit.inventory,
        })
        logger.debug('Unit %d grabbed %d %s' % (unit.uid, amount, item.typename))

    def unit_idle(self, unit):
        self.curround.change(unit.uid, {
            'intent': 'idle',
        })
        pass

    def unit_move(self, unit, pos):
        dx = pos[0] - unit.pos[0]
        dy = pos[1] - unit.pos[1]
        direction = self.world.calc_direction(dx, dy)
        intent = 'idle'
        if direction:
            intent = 'move' + direction
        dist = sqrt(dx ** 2 + dy ** 2)
        if dist > unit.running_speed:
            scale = unit.running_speed / dist
            x = dx * scale + unit.pos[0]
            y = dy * scale + unit.pos[1]
            pos = (x, y)
        newpos = self.world.cd.get_pos(unit.pos, pos, unit.size)
        logger.debug('Unit %d moved from %s to %s' % (unit.uid,
                          str(unit.pos), str(newpos)))
        self.curround.change(unit.uid, {
            'pos': unit.pos,
            'intent': intent,
        })
        unit.pos = newpos

    def unit_spawn(self, unit, typename):
        # Make sure the unit is allowed to spawn this typename
        min_level = get_unit_property(typename, 'min_user_level')
        if unit.player.level < min_level:
            unit.player.log('You must be at least level %d to spawn a %s' %
                           (min_level, typename), 'warning')
            return
        # If the unit is still waiting to spawn
        if unit.rounds_committed:
            logger.debug('%d rounds until spawn' % unit.rounds_committed)
            return
        # If the unit has finished the waiting period
        if unit.rounds_committed == 0:
            # TODO: this pos may not be valid if a unit is spawning something
            # larger than itself
            pos = self.world.randomize_pos(unit.pos, unit.size, 20)
            self.add_unit(typename, unit.player, pos)
            logger.debug('adding unit')
            return
        # If the unit is just begining to spawn
        for itemtype, needed in unit.spawn_items_req[typename].items():
            if unit.inventory.get(itemtype, 0) < needed:
                unit.player.log("You don't have enough %s to spawn a %s" %
                               (itemtype, typename), 'warning')
                return
        for itemtype, needed in unit.spawn_items_req[typename].items():
            self.modify_inventory(unit, itemtype, -needed)
        unit.rounds_committed = int(ceil(unit.spawn_time_req[
                    typename] / float(time_per_round)))
        self.curround.change(unit.uid, {
            'intent': 'spawn',
            'inventory': unit.inventory,
        })
        logger.debug('Unit %d is spawning a %s' % (unit.uid, typename))

    def inc(self):
        dead_units = []
        for unit in self.world.units.values():
            if 'health_drain' in unit.effects:
                unit.health -= unit.effects['health_drain'] * time_per_round
                self.curround.change(unit.uid, {'health': unit.health})
            if unit.health < 1:
                dead_units.append(unit)
        for unit in dead_units:
            self.unit_die(unit)
        in_progress = True
        if (len(self.players) < 2 or self.round_num * time_per_round >
                self.max_time):
            in_progress = False
            self.curround['end'] = True
            for player in self.players.values():
                player.final_round = self.round_num + 1
                self.dead_players[player.uid] = player
                player.units.clear()
            for unit in list(self.world.units.values()):
                self.curround.change(unit.uid, {'intent': 'idle',})
                unit.kill()
        self.round_num += 1
        self.world.inc()
        return in_progress

    def kill(self):
        for unit in self.world.units.values():
            unit.kill()
