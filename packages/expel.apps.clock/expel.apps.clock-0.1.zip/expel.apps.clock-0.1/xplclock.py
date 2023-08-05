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

import datetime

from expel.message.xpl import xPLStatus, xPLTrigger
from expel.lib.looper import xPLLooper

__all__ = ['xPLClock']


class xPLClock(xPLLooper):
    """xPL Clock - Sends out datetime.basic information every `tick` minutes."""
    
    def __init__(self):
        xPLLooper.__init__(self)

        self.vendor = 'sffj'
        self.device = 'clock'
        self.title = 'xPL Clock'

        self.MessageReceived += self.message_received
        self.ConfigChanged += self.config_changed
        self.StateChanged += self.state_changed

        self._tick = 1

    def state_changed(self, *args, **kwargs):
        if args[1] == xPLLooper.PROBE_FOR_HUB:
            self.reactor.call_later(0.1, self._loop, init=True)

    def message_received(self, msg, *args, **kwargs):
        msg_type = msg.message_type.lower()
        schema_class = msg.schema_class.lower()
        schema_type = msg.schema_type.lower()

        if msg_type == 'cmnd':
            try:
                if schema_class == 'datetime' and schema_type == 'request':
                    command = msg['command'].strip().lower()
                    
                    if command == 'status':
                        reply = xPLStatus(self.source)
                        reply.schema_class = 'datetime'
                        reply.schema_type = 'basic'
                        
                        now = datetime.datetime.now()
                        d = '%d%02d%02d' % (now.year, now.month, now.day)
                        t = '%02d%02d%02d' % (now.hour, now.minute,
                            now.second)

                        reply['datetime'] = '%s%s' % (d, t)
                        
                        self.broadcast_message(reply)
                        
            except:
                pass

    def config_changed(self, msg, *args, **kwargs):
        try:
            value = int(self.config['tick'].value)
            self._tick = tick
        except:
            pass

    def _loop(self, init=False):
        """The main loop."""

        if init == True:
            self._datetime = datetime.datetime.now().replace(second=0, 
                microsecond=0)
        
        now = datetime.datetime.now()
        td = now - self._datetime
        minutes = td.seconds / 60
            
        if minutes >= self._tick:
            msg = xPLTrigger(self.source)
            msg.schema_class = 'datetime'
            msg.schema_type = 'basic'
            
            d = '%d%02d%02d' % (now.year, now.month, now.day)
            t = '%02d%02d%02d' % (now.hour, now.minute, now.second)

            msg['datetime'] = '%s%s' % (d, t)
            msg['date'] = '%s' % d
            msg['time'] = '%s' % t
            
            self.broadcast_message(msg)
            
            self._datetime = now

        self.reactor.call_later(1, self._loop)


if __name__ == '__main__':
    x = xPLClock()
    x()
