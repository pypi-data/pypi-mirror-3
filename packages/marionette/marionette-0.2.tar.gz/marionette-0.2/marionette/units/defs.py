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
from ..defs import create_base_data, create_defs


__all__ = (
    'isunittype',
    'get_unit_property',
    'get_unit_typenames',
    'get_unit_upgrades',
)


_defs = create_defs('units')
_base_data = create_base_data('units')
_available_actions = {}
_base_properties = {}
for typename, typedefs in _defs.items():
    actions = []
    properties = {}

    # Get defualt values for upgradeable properties
    for attribute in typedefs['attributes']:
        actions.extend(_base_data['actions'].get(attribute, []))
        properties.update(_base_data['values'].get(attribute, {}))

    # Override the default value with level 0 of an upgrade type
    for upgrades in typedefs['upgrades'].values():
        properties.update(upgrades[0])

    _available_actions[typename] = set(actions)
    _base_properties[typename] = properties


def get_available_actions(typename):
    return _available_actions[typename]


def get_unit_property(typename, attribute):
    return _defs[typename][attribute]


def get_unit_properties(typename):
    return _defs[typename].items()


def get_unit_upgrades(typename):
    return _defs[typename]['upgrades']


def get_base_properties(typename):
    return _base_properties[typename]


def isunittype(typename):
    return typename in _defs


def get_unit_typenames():
    return list(_defs.keys())
