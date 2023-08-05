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
from .colorlist import (attr_in_colorlist, kw_blacklist, kw_graylist,
                        mod_whitelist, mod_whitelist_prefixes)
from ast import (Assign, Attribute, Call, ClassDef, Dict, Import, ImportFrom,
                 List, Name, Return, Set, Tuple, Yield, alias, arguments,
                 parse as ast_parse, walk)
from collections import defaultdict
import ast


class ParseError(Exception):
    def __init__(self, msg=None, row=None, col=None):
        self.msg = msg
        self.row = row
        self.col = col

    def __repr__(self):
        params = []
        for attr in ('msg', 'row', 'col'):
            if getattr(self, attr) == None:
                break
            params.append(str(getattr(self, attr)))
        return 'ParseError(%s)' % ', '.join(params)

    def __str__(self):
        ret = self.msg
        if self.row:
            ret += ' (row: %d' % self.row
            if self.col:
                ret += ' col: %d' % self.col
            ret += ')'
        return ret


def parse_individual_attrs(root):
    """Parse the names and attributes from farthest to nearest
    a.b.c -> c, b, a

    """
    node = root
    while isinstance(node, Attribute):
        yield node.attr
        node = node.value
    if isinstance(node, Name):
        yield node.id


def parse_attr(root):
    """Returns an empty string if there is no attr"""
    return '.'.join(reversed(list(parse_individual_attrs(root))))


def parse_import(root):
    """Parse an Import or ImportFrom node

    Returns a dict mapping symbols to a list of attributes it may correspond
    to.

    """
    ret = defaultdict(list)
    prefix = ''
    if isinstance(root, ImportFrom):
        prefix = '.' * root.level
        if root.module:
            prefix += root.module + '.'
    for node in walk(root):
        if isinstance(node, alias):
            ret[node.asname or node.name].append(prefix + node.name)
    return ret


def is_nonrestricted_module(attr, mod_whitelist=mod_whitelist,
                            mod_whitelist_prefixes=mod_whitelist_prefixes):
    """This tells us if a module is whitelisted or may be expanded to a
    whitelisted module

    """
    return (attr in mod_whitelist_prefixes or
            attr_in_colorlist(attr, mod_whitelist))


def parse_imports(root, mod_whitelist=mod_whitelist,
                  mod_whitelist_prefixes=mod_whitelist_prefixes):
    """Get all the imports in the tree.

    Returns a dictionary mapping symbols to lists of modules that may be used
    improperly.

    Throws an error if an import is not whitelisted and has no whitelisted
    expansion.

    """
    ret = defaultdict(list)
    for node in walk(root):
        if isinstance(node, Import) or isinstance(node, ImportFrom):
            mods = parse_import(node)
            for mod_list in mods.values():
                for mod in mod_list:
                    if not is_nonrestricted_module(
                        mod, mod_whitelist=mod_whitelist,
                        mod_whitelist_prefixes=mod_whitelist_prefixes):
                        msg = 'You are not allowed to import "%s"' % mod
                        raise ParseError(msg, node.lineno, node.col_offset)
            if '*' in mods:
                del mods['*']
            for key, value in mods.items():
                ret[key] += value
    return ret


def alias_expansions(attr, table):
    for alias in table:
        if attr.startswith(alias):
            for value in table[alias]:
                yield attr.replace(alias, value, 1)


def is_whitelisted_expansion(attr, mod_whitelist=mod_whitelist, mod_table={}):
    for expansion in alias_expansions(attr, mod_table):
        if not attr_in_colorlist(expansion, mod_whitelist):
            return False
    return True


def parse_assignment(node, kw_graylist=kw_graylist,
                     mod_whitelist=mod_whitelist, mod_table={}):
    """Parses something that may be a Name or Attribute used in an assignment

    Return False if it's dangerous.

    """
    # For modules, we are going beyond what we defined as "protected symbols"
    # because this will reject nonwhitelisted modules that can't be expanded to
    # whitelisted modules as well as ones that can.
    if not is_whitelisted_expansion(parse_attr(node), mod_whitelist,
                                    mod_table):
        return False
    for attr in parse_individual_attrs(node):
        if attr in kw_graylist:
            return False
    return True


def parse_assignments(root, kw_graylist=kw_graylist,
                      mod_whitelist=mod_whitelist, mod_table={}):
    """Go through the tree and parse anything that can cause an improper
    alias.

    Returns True if it parses correctly.

    Throws an error if there is an attempt to alias a nonwhitelisted module
    attribute or a graylisted keyword.

    """
    node_types = {
        List: ([('elts', True)], 'put "%s" in a list'),
        Tuple: ([('elts', True)], 'put "%s" in a list'),
        Set: ([('elts', True)], 'put %s in a set'),
        Dict: ([('keys', True), ('values', True)], 'put "%s" in a dict'),
        Call: ([('args', True)], 'pass "%s" as a parameter to a function'),
        ClassDef: ([('bases', True)], 'use "%s" as a base class'),
        arguments: ([('defaults', True)], 'use "%s" as a default argument'),
        Assign: ([('value', False)], 'assign "%s" to a different variable'),
        Return: ([('value', False)], 'return "%s"'),
        Yield: ([('value', False)], 'yield "%s"'),
    }
    for node in walk(root):
        node_type = node_types.get(type(node))
        if node_type:
            for target, multiple in node_type[0]:
                values = getattr(node, target)
                if not multiple:
                    values = [values]
                for value in values:
                    if not parse_assignment(value, kw_graylist=kw_graylist,
                                            mod_whitelist=mod_whitelist,
                                            mod_table=mod_table):
                        err_type = node_type[1] % parse_attr(value)
                        msg = 'You are not allowed to %s' % err_type
                        row = getattr(node, 'lineno', None)
                        col = getattr(node, 'col_offset', None)
                        raise ParseError(msg, row, col)
    return True


def is_nonrestricted_expansion(attr,  mod_whitelist=mod_whitelist,
                               mod_whitelist_prefixes=mod_whitelist_prefixes,
                               mod_table={}):
    for expansion in alias_expansions(attr, mod_table):
        if not is_nonrestricted_module(expansion, mod_whitelist,
                                       mod_whitelist_prefixes):
            return False
    return True


def parse_load(node, kw_blacklist=kw_blacklist, mod_whitelist=mod_whitelist,
               mod_whitelist_prefixes=mod_whitelist_prefixes, mod_table={}):
    """We may have a Name or an Attribute

    return True if it's ok.

    """
    attr = parse_attr(node)
    if attr and not is_nonrestricted_expansion(attr, mod_whitelist,
                                               mod_whitelist_prefixes,
                                               mod_table):
        return False
    for attr in parse_individual_attrs(node):
        if attr in kw_blacklist:
            return False
    return True


def parse_loads(root, kw_blacklist=kw_blacklist, mod_whitelist=mod_whitelist,
                mod_whitelist_prefixes=mod_whitelist_prefixes, mod_table={}):
    for node in walk(root):
        if not parse_load(node, kw_blacklist=kw_blacklist,
                          mod_whitelist=mod_whitelist,
                          mod_whitelist_prefixes=mod_whitelist_prefixes,
                          mod_table=mod_table):
            msg = 'You are not allowed to use "%s"' % parse_attr(node)
            raise ParseError(msg, node.lineno, node.col_offset)
    return True


def parse(code, kw_blacklist=kw_blacklist, kw_graylist=kw_graylist,
          mod_whitelist=mod_whitelist,
          mod_whitelist_prefixes=mod_whitelist_prefixes):
    """
    A "protected symbol" is a nonwhitelisted module that expands to a
        whitelisted module or graylisted keyword
    A "restricted symbol" is a nonwhitelisted module that does not expand to
        whitelisted module or a blacklisted keyword

    This makes sure that the code does none of the following:
    * (0) Generate syntax errors
          - This is not strictly necessary but we do it for usability
    * (1) Import an attr that is not whitelisted and has no whitelisted
          expansion (Import.names, ImportFrom.names)
          - This is not strictly necessary but we do it for usability
    * (2) Do any of the following to a protected symbol:
        * (a) Wrap it up in [], (), {}
              (List.elts, Tuple.elts, Set.elts, Dict.keys, Dict.values)
        * (b) Pass it as a parameter to a function (Call.args)
              - This covers decorators
        * (c) Use it as a base class (ClassDef.bases)
        * (d) Alias it - we do allow aliasing in import statements
              (Assign.value)
              - with is safe
        * (e) Use it as a default parameter (arguments.defaults)
        * (f) Return it (Return.value, Yield.value)
              - Do not need to worry about raise
    * (3) Use a restricted symbol

    We do not pay attention to context so what we call "protected symbols" or
    "restricted symbols" may or may not be dangerous.  It's typically a bad
    idea to call other things by these names anyway.

    NOTE: This will not prevent code from doing module.__file__ and learning
    the location of the modules.

    """
    # (0) Parse the code
    try:
        root = ast_parse(code)
    except SyntaxError as e:
        raise ParseError('Syntax error', e.lineno)

    # (1) Walk through once to get the imports
    imports = parse_imports(root)

    # (2) Go through again and moderate the protected symbols
    parse_assignments(root, kw_graylist=kw_graylist,
                      mod_whitelist=mod_whitelist, mod_table=imports)

    # (3) Go through again and moderate the restricted symbols
    parse_loads(root, kw_blacklist=kw_blacklist, mod_whitelist=mod_whitelist,
                mod_whitelist_prefixes=mod_whitelist_prefixes,
                mod_table=imports)

    return True
