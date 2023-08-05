#!/usr/bin/env python
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
# Setup files are plain.
# Only values do they contain.
#     They avoid fancy function
#     As per unspoken injunction,
# Except ours, which is flippin' insane.
#
from distutils.core import setup


setup(
    name='marionette',
    version='0.2',
    description='AI game for the net',
    long_description='AI game for the net',
    author='Conley Owens',
    author_email='cco3@inkylabs.com',
    url='http://mutantmarionette.com/',
    packages=[
        '',
        'marionette',
        'marionette.commands',
        'marionette.items',
        'marionette.obstacles',
        'marionette.replay',
        'marionette.sanitization',
        'marionette.units',
        'marionette.utils',
    ],
    package_data={'': [
            'LICENSE',
        ], 'marionette.items': [
            'defs/*',
        ], 'marionette.replay': [
            'web/favicon.ico',
            'web/img/load.gif',
            'web/img/backgrounds/*',
            'web/img/items/*',
            'web/img/units/*',
            'web/index.html',
            'web/js/replay/*.js',
            'web/js/replay.js',
            'web/js/third_party/*.js',
        ], 'marionette.sanitization': [
            'defs/*',
        ], 'marionette.units': [
            'defs/*',
        ],
    },
    scripts=[
        'scripts/marionette',
    ],
    license='Apache2.0',
    platforms=['GNU/Linux']
)
