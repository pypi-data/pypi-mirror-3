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
from .obstacles import Obstacle
from .utils.spatial import Rect, overlaps

from math import ceil, sqrt
from random import randint


class CollisionDetector(object):

    """

    Holds information about rectangular objects and their velocities and
    detects collisions.

    Currently, this is done by partitioning all solid objects into tiles.
    For a moving object that may hit a solid object, we get a bounding box
    around its trajectory to get a superset of all tiles it may pass through.
    We then pair it with all objects in those tiles to see where a collision
    may occur.

    """

    def __init__(self, worldsize, tilesize=(32, 32)):
        self.worldsize = worldsize
        self.tilesize = tilesize
        numtiles = [0, 0]
        for i in range(2):
            numtiles[i] = int(ceil(self.worldsize[i] / self.tilesize[i]))
        self.tiles = []
        for i in range(numtiles[0]):
            self.tiles.append([[] for i in range(numtiles[1])])
        self.objects = []
        self.cur_id = 0

    def _calc_tiles(self, pos1, pos2, size):
        """Get the tiles that our object may pass through.

        Currently this may be a superset of the actual tiles it passes through.

        """
        # Get the bounding box of the trajectory
        mintile = [0, 0]
        maxtile = [0, 0]
        for i in range(2):
            minpos = max(min(pos1[i], pos2[i]), 0)
            mintile[i] = int(minpos / self.tilesize[i])
            maxpos = max(pos1[i] + size[i] - 1, pos2[i] + size[i] - 1)
            maxpos = min(maxpos, self.worldsize[i] - 1)
            maxtile[i] = int(maxpos / self.tilesize[i])

        # Yield the tiles
        for i in range(mintile[0], maxtile[0] + 1):
            for j in range(mintile[1], maxtile[1] + 1):
                yield self.tiles[i][j]

    def _corners(self, pos, size):
        yield pos
        yield pos[0] + size[0] - 1, pos[1]
        yield pos[0], pos[1] + size[1] - 1
        yield pos[0] + size[0] - 1, pos[1] + size[1] - 1

    def _path(self, pos1, pos2):
        delta = (pos2[0] - pos1[0], pos2[1] - pos1[1])
        dist = sqrt(delta[0]**2 + delta[1]**2)
        if dist == 0.0:
            return
        unit_vect = (delta[0] / dist, delta[1] / dist)
        # We want to take exactly 1 less than the steps needed before
        # yielding the final position outside of the loop
        steps = int(dist) if dist == int(dist) else int(dist) + 1
        for i in range(1, steps):
            yield (pos1[0] + i * unit_vect[0], pos1[1] + i * unit_vect[1])
        yield pos2

    def add(self, pos, size):
        rect = Obstacle(pos, size)
        self.objects.append(rect)
        tiles = self._calc_tiles(pos, pos, size)
        for tile in tiles:
            tile.append(rect)

    def _fix_overlap(self, pos1, size1, pos2, size2, delta):
        # Find the amount of x and y overlap
        new_delta = [0, 0]
        for i in range(2):
            if delta[i] > 0:
                new_delta[i] = pos1[i] + size1[i] - pos2[i]
            elif delta[i] < 0:
                new_delta[i] = pos1[i] - (pos2[i] + size2[i])

        # If one direction doesn't change, we move in the other one
        if delta[0] == 0:
            return (pos1[0], pos1[1] - new_delta[1])
        if delta[1] == 0:
            return (pos1[0] - new_delta[0], pos1[1])

        # Decide which axis we should correct our overlap on to cause
        # the smallest change in position.
        if new_delta[0] / delta[0] > new_delta[1] / delta[1]:
            new_delta[0] = delta[0] * new_delta[1] / delta[1]
        else:
            new_delta[1] = delta[1] * new_delta[0] / delta[0]

        return (pos1[0] - new_delta[0], pos1[1] - new_delta[1])

    def pos_is_valid(self, pos, size):
        tiles = self._calc_tiles(pos, pos, size)
        for tile in tiles:
            for rect in tile:
                if overlaps(Rect(pos, size), rect):
                    return False
        return True

    def get_pos(self, pos1, pos2, size):
        delta = (pos2[0] - pos1[0], pos2[1] - pos1[1])
        rects = []
        for tile in self._calc_tiles(pos1, pos2, size):
            rects += tile
        hit = False
        for p in self._path(pos1, pos2):
            for rect in rects:
                if overlaps(Rect(p, size), rect):
                    hit = True
                    p = self._fix_overlap(p, size, rect.pos, rect.size, delta)
            if hit:
                return p
        return pos2
