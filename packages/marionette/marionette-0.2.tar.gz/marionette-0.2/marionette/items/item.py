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
from .defs import get_item_properties


__all__ = (
    'Item',
)


class Item(object):
    def __init__(self, typename, pos, amount, uid=0):
        for key, value in get_item_properties(typename):
            setattr(self, key, value)
        self.pos = pos
        self.amount = amount
        self.uid = uid

    @property
    def weight(self):
        return self.weight_per_unit * self.amount

    def __getstate__(self):
        ret = {}
        public_attrs = (
            'amount',
            'pos',
            'size',
            'typename',
            'uid',
            'weight_per_unit',
        )
        for key in public_attrs:
            if hasattr(self, key):
                ret[key] = getattr(self, key)
        return ret

    def __str__(self):
        return '%s:%d%s' % (self.typename, self.amount, str(self.pos))
