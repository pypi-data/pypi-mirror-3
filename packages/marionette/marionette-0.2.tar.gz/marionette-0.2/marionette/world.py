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
from .collision import CollisionDetector
from .items import Item, get_item_property
from .utils.spatial import distance as calc_distance

from math import atan, cos, pi, sin, sqrt
from random import gauss, randint, uniform as randfloat


class World(object):
    def __init__(self, width, height, uid_manager):
        self.uid_manager = uid_manager
        self.orig = (randint(-2 ** 31, 2 ** 31),
                     randint(-2 ** 31, 2 ** 31))
        self.width = width
        self.height = height
        self.time = 0
        self.items = {}
        self.units = {}
        self._distances = {}
        self.cd = CollisionDetector((width, height))
        self.cd.add((0, 0), (width, 1))
        self.cd.add((0, height - 1), (width, 1))
        self.cd.add((0, 0), (1, height))
        self.cd.add((width - 1, 0), (1, height))
        #self.generate_obstacles()

    def inc(self):
        # Decide how many piles of grutonium to make this round
        for i in range(int(abs(gauss(0, .7)))):
            if len(self.items) <= 50:
                self.make_item('grutonium')
        self.time += 1
        self._distances = {}

    def calc_direction(self, dx, dy):
        if dx == 0 and dy == 0:
            return
        try:
            slope = float(dy) / dx
        except ZeroDivisionError:
            slope = float('inf')
        # Angle ranges from [0, 2) where 0 = north, .5 = east, 1 = south,
        # and 1.5 = west.
        angle = (atan(slope) / pi) + .5
        if dx <= 0:
            angle += 1
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        direction = 'N'
        if angle < 1.875:
            direction = directions[round(angle * 4)]
        return direction

    def make_item(self, itemtype, amount=None, pos=None):
        # TODO: When we have obstacles, the initial position isn't
        #       necessarily valid.
        size = get_item_property(itemtype, 'size')
        uid = self.uid_manager.generate()
        if not pos:
            pos = self.place_random(size)
        if not amount:
            amount = int(abs(gauss(0, 2))) + 1
        self.items[uid] = Item(itemtype, pos, amount, uid)
        self.curround.change(uid, {
            'amount': amount,
            'type': itemtype,
            'pos': pos
        })

    def randomize_pos(self, origin, size, radius):
        # TODO: Potentially problematic if a unit drops/spawns something bigger
        #       than itself, because the initial position isn't necessarily
        #       valid.
        dr = randfloat(0, radius)
        theta = randfloat(0, 2 * pi)
        dx = dr * cos(theta)
        dy = dr * sin(theta)
        pos = (origin[0] + dx, origin[1] + dy)
        return self.cd.get_pos(origin, pos, size)

    def generate_obstacles(self, num_obstacles=20):
        for i in range(num_obstacles):
            size = (choice(40, 80), choice(30, 60))
            pos = self.place_random(size)
            self.cd.add(pos, size)

    def place_random(self, size):
        while True:
            pos = (randint(0, self.width - size[0] - 1),
                   randint(0, self.height - size[1] - 1))
            if self.cd.pos_is_valid(pos, size):
                return pos

    def distance(self, obj1, obj2):
        key = '%d-%d' % tuple(sorted([obj1.uid, obj2.uid]))
        if key not in self._distances:
            self._distances[key] = calc_distance(obj1, obj2)
        return self._distances[key]
