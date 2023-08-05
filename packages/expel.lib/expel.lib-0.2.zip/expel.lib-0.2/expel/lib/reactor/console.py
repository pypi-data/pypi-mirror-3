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

from twisted.internet import reactor

import signal

class consoleReactor(object):
    def __init__(self):
        self.looper = None
    
    def run(self):
        """Start the reactor"""

        # Setup signal handlers
        self._old_int_handler = signal.signal(signal.SIGINT, self.stop)
        self._old_term_handler = signal.signal(signal.SIGTERM, self.stop)
        
        # SIGBREAK is Windows specific so catch exception on other OSes
        try:
            self._old_break_handler = signal.signal(signal.SIGBREAK, self.stop)
            self._break_installed = True
        except AttributeError:
            self._break_installed = False

        reactor.run(installSignalHandlers=0)

    def listen(self, looper):
        """Start listening for messages to the looper."""
        self.looper = looper
        reactor.listenUDP(looper.port, looper, looper.address)

    def call_later(self, delay, func, *args, **kwargs):
        reactor.callLater(delay, func, *args, **kwargs)

    def call_when_running(self, func, *args, **kwargs):
        reactor.callWhenRunning(func, *args, **kwargs)

    def stop(self, sn=None, sf=None):
        """Stop the reactor

        Called either by the xPLLooper or via the SIGINT, SIGTERM or SIGBREAK
        signal handler. ``sn`` and ``sf`` parameters required by signal.signal"""

        self.looper._stop()
        reactor.stop()

        # Restore original signal handlers
        signal.signal(signal.SIGINT, self._old_int_handler)
        signal.signal(signal.SIGTERM, self._old_term_handler)
        
        if self._break_installed:
            signal.signal(signal.SIGBREAK, self._old_break_handler)

