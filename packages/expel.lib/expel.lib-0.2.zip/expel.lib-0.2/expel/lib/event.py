# Copyright (c) 2009-2011 Simon Kennedy <code@sffjunkie.co.uk>.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__all__ = ['xPLEvent']

class xPLEvent(object):
    """
    xPLEvent class maintains a list of xPLEventHandlers which are called
    with the parameters passed to the xPLEvent.__call__ function.
    """
    
    def __init__(self, looper):
        self._looper = looper
        self._handlers = []

    def __call__(self, msg, *args, **kwargs):
        for handler in self._handlers:
            handler(msg, looper=self._looper, *args, **kwargs)

    def __iadd__(self, handler):
        return self.add_handler(handler)

    def __isub__(self, handler):
        return self.remove_handler(handler)

    def add_handler(self, handler):
        self._handlers.append(handler)
        return self

    def remove_handler(self, handler):
        if handler in self._handlers:
            self._handlers.remove(handler)
        return self
