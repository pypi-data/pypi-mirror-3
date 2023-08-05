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
from ..defs import create_defs


__all__ = (
    'isitemtype',
    'get_item_property',
)
_defs = create_defs('items')


def get_item_property(typename, attribute):
    return _defs[typename][attribute]


def get_item_properties(typename):
    return _defs[typename].items()


def isitemtype(typename):
    return typename in _defs
