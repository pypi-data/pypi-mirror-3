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
from logging import ERROR, Formatter, StreamHandler, getLogger


__all__ = ()


logger = getLogger(__name__)
log_handler = StreamHandler()
fmt = '%(asctime)s %(levelname)s %(name)s %(message)s'
log_formatter = Formatter(fmt=fmt)
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)
logger.setLevel(ERROR)


# A bunch of hacks to hide errors when we keyboard interrupt
import sys
if hasattr(sys, 'modules'):
    from multiprocessing.managers import BaseManager, BaseProxy
    _old_after_fork = BaseProxy._after_fork
    def _new_after_fork(self):
        try:
            _old_after_fork(self)
        except KeyboardInterrupt:
            pass
    sys.modules['multiprocessing.managers'].BaseProxy._after_fork = \
            _new_after_fork

    # We shouldn't really need this one.  For some reason, the callback
    # loses access to classes and function defined in its own module
    # when we use Sandbox in the main (parent) process.
    _old_decref = BaseProxy._decref
    def _new_decref(*args, **kwargs):
        if not _old_decref:
            return
        try:
            _old_decref(*args, **kwargs)
        except AttributeError:
            pass
    sys.modules['multiprocessing.managers'].BaseProxy._decref = _new_decref
