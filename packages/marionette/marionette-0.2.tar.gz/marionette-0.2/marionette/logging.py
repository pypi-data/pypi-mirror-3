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
# So your code has started to break,
# And you want to locate your mistake.
#     Don't get in a tiff,
#     You'll be done in a jiff,
# And it'll be a piece of cake.
#
__all__ = (
    'debug',
    'info',
    'warning',
    'error',
    'critical',
)
_log_data = None


def _log(args, lvl):
    # _log_data may not be set in cases where we are just loading code to
    # ensure it runs, and not actually playing a game.
    if _log_data == None:
        return
    limit = 20 * 1250
    msg = ' '.join(map(str, args))
    if len(msg) > limit:
        msg = ('LogError: The string you are trying to log is longer '
               'than %d characters.' % limit)
    _log_data.append((msg, lvl))

def debug(*args):
    _log(args, 'debug')

def info(*args):
    _log(args, 'info')

def warning(*args):
    _log(args, 'warning')

def error(*args):
    _log(args, 'error')

def critical(*args):
    _log(args, 'critical')
