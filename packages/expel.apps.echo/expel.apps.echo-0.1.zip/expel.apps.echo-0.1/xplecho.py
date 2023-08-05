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

from expel.lib.looper import xPLLooper

class xPLEcho(xPLLooper):
    """xPL Echo - Echos all messages received from the xPL hub."""

    def __init__(self):
        xPLLooper.__init__(self)

        self.vendor = 'sffj'
        self.device = 'echo'
        self.title = 'xPL Echo'
        
        self.MessageReceived += self.message_received

    def message_received(self, msg, *args, **kwargs):
        if self.logger is not None:
            self.logger.info('%s: %s' % (self.title, repr(msg)))


if __name__ == '__main__':
    x = xPLEcho()
    x()
