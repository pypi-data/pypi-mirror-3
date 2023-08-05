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
from ..items import Item
from .defs import (get_available_actions, get_base_properties,
                   get_unit_upgrades)

from copy import copy
from json import dumps, loads
from logging import getLogger
from multiprocessing.managers import RemoteError
from re import compile as re_compile
from socket import error as socket_error
from time import time
from types import MethodType


__all__ = (
    'ParamError',
    'Unit',
    'copy_values',
    'resolve_attributes',
    'verify_action',
)
logger = getLogger(__name__)


class ParamError(Exception):
    pass


_action_params = {
    'attack': {'uid'},
    'die': {},
    'drop': {'typename', 'amount'},
    'eat': {'typename', 'amount'},
    'grab': {'uid', 'amount'},
    'idle': {},
    'move': {'pos'},
    'spawn': {'typename'},
}
_param_types = {
    'amount': 'posint',
    'typename': 'str',
    'uid': 'posint',
    'pos': 'pos',
}
def verify_action(action_data, typename):
    """Tell if data matches an action, changing types if necessary.

    Ex: move {'pos': [10]} is invalid because it's missing y.

    """
    # Verify the data
    if type(action_data) != tuple or len(action_data) != 2:
        raise ParamError('return type of act must be a tuple of size 2')
    action, data = action_data

    # Verify the action name
    if type(action) != str:
        raise ParamError('action name must be a str')
    if action not in get_available_actions(typename):
        raise ParamError('action must be one of %s' %
                         ', '.join(get_available_actions(typename)))

    # Verify the parameters
    if type(data) != dict:
        raise ParamError('attempted to send parameters'
                         'in non-dictionary format')
    for key in data:
        if type(key) != str:
            raise ParamError('key to arguments must be a string')
    if set(data.keys()) != _action_params[action]:
        raise ParamError('parameters to %s should be %s'
                         % (action, ', '.join(_action_params[action])))
    for key, value in data.items():
        param_type = _param_types[key]
        if param_type == 'pos':
            if type(value) not in (tuple, list) or len(value) != 2:
                raise ParamError('%s must be a tuple or list of size 2' % key)
            if (type(value[0]) not in (float, int) or
                type(value[1]) not in (float, int)):
                raise ParamError('%s must be a tuple of floats or integers' %
                                 key)
        elif param_type == 'posint':
            if type(value) != int or value < 0:
                raise ParamError('%s must be a positive integer' % key)
        elif key == 'str':
            if type(value) != str:
                raise ParamError('%s must be a string', key)


def initialize_values(data, values):
    """Given a dictionary, initialized attributes"""
    for k, v in values.items():
        data[k] = copy(v)


def encoded_pos(pos, origin):
    return (pos[0] + origin[0], pos[1] + origin[1])


def decoded_pos(pos, origin):
    return (pos[0] - origin[0], pos[1] - origin[1])


def copy_values(data1, data2, keys):
    """Given two dictionaries, copies attributes"""
    origin = None
    try:
        if 'origin' in data1:
            origin = data1['origin']
    except socket_error:
        logger.warn('Error getting origin')
    for k in keys:
        value = None
        try:
            value = data1[k]
        except socket_error:
            logger.warn('Error getting attribute ' + k)
        if origin:
            if k == 'items_in_view':
                items = []
                for item in value:
                    items.append(Item(typename=item.typename,
                                      pos=encoded_pos(item.pos, origin),
                                      amount=item.amount,
                                      uid=item.uid))
                value = items
            elif k == 'units_in_view':
                units = []
                for unit in value:
                    to_append = Unit()
                    public_attrs = (
                        'health',
                        'max_health',
                        'player',
                        'pos',
                        'size',
                        'typename',
                        'uid',
                    )
                    for attr in public_attrs:
                        if hasattr(unit, attr):
                            uval = getattr(unit, attr)
                            if attr == 'pos':
                                uval = encoded_pos(uval, origin)
                            elif attr == 'player':
                                uval = uval.uid
                            setattr(to_append, attr, uval)
                    units.append(to_append)
                value = units
            elif k == 'pos':
                value = encoded_pos(value, origin)
        try:
            data2[k] = value
        except (EOFError, IOError, RemoteError, socket_error):
            logger.warn('Error copying attribute ' + k)


def resolve_attributes(typename, selected_upgrades):
    attributes = copy(get_base_properties(typename))
    for upgradetype, upgradeset in get_unit_upgrades(typename).items():
        for i in range(1, selected_upgrades.get(upgradetype, 0) + 1):
            attributes.update(upgradeset[i])
    return attributes


class Unit:
    def act(self):
        """Unit implementations should override this with something smarter."""
        from .. import logging
        logging.error('act() is not implemented')
        return ('idle', {})
