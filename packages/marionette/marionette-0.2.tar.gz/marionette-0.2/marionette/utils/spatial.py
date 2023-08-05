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
from math import sqrt


__all__ = (
    'Rect',
    'autorect',
    'distance',
    'nearest_point',
    'nearest_points',
    'overlaps',
)


class Rect:
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size


def autorect(o):
    if type(o) == tuple:
        return Rect(o, (1, 1))
    return o


def nearest_points(o1, o2):
    o1, o2 = autorect(o1), autorect(o2)

    # Get x
    w1, w2 = o1.pos[0], o2.pos[0]
    e1, e2 = o1.pos[0] + o1.size[0] - 1, o2.pos[0] + o2.size[0] - 1
    if e1 < w2:  # o1 is strictly west of o2
        x1, x2 = e1, w2
    elif e2 < w1:  # o2 is strictly west of o1
        x1, x2 = w1, e2
    else:
        if w1 < w2:
            x1, x2 = w2, w2
        else:
            x1, x2 = w1, w1

    # Get y
    n1, n2 = o1.pos[1], o2.pos[1]
    s1, s2 = o1.pos[1] + o1.size[1] - 1, o2.pos[1] + o2.size[1] - 1
    if s1 < n2:  # o1 is strictly north of o2
        y1, y2 = s1, n2
    elif s2 < n1:  # o2 is strictly north of o1
        y1, y2 = n1, s2
    else:
        if n1 < n2:
            y1, y2 = n2, n2
        else:
            y1, y2 = n1, n1

    return (x1, y1), (x2, y2)


def nearest_point(o1, o2):
    """Gets the closest point of o2 to o1

    Each parameter should either be a position tuple or an object with
    a .pos and .size

    """
    nearest_points(o1, o2)[1]


def distance(o1, o2):
    """Calculate the cartesion distance between objects or points

    Each parameter should either be a position tuple or an object with
    a .pos and .size

    """
    p1, p2 = nearest_points(o1, o2)
    dx, dy = p1[0] - p2[0], p1[1] - p2[1]
    return sqrt(dx ** 2 + dy ** 2)


def overlaps(o1, o2):
    """Calculate whether two objects are overlapping

    Each parameter should either be a position tuple or an object with
    a .pos and .size
    """
    o1, o2 = autorect(o1), autorect(o2)
    # If the objects don't overlap in the x or y axis, return False
    for i in range(2):
        if not (o2.pos[i] <= o1.pos[i] < o2.pos[i] + o2.size[i] or
                o1.pos[i] <= o2.pos[i] < o1.pos[i] + o1.size[i]):
            return False
    return True
