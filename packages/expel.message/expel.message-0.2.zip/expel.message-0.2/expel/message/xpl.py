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

from xmessage import xMessage, xMessageBlock
from xmessageparser import xMessageParser

__all__ = ['xPLMessage', 'xPLHBeatBasic', 'xPLHBeatApp',
    'xPLHBeatRequest', 'xPLHBeatEnd',
    'xPLCommand', 'xPLStatus', 'xPLTrigger']


class xPLMessageError(Exception):
    pass


class xPLMessage(xMessage):
    XPL_HDR_RAW  = '\n{\nhop=1\nsource=%s\ntarget=*\n}\n'
    XPL_CMND_RAW = 'xpl-cmnd' + XPL_HDR_RAW
    XPL_STAT_RAW = 'xpl-stat' + XPL_HDR_RAW
    XPL_TRIG_RAW = 'xpl-trig' + XPL_HDR_RAW

    HBEAT_BASIC_RAW  = XPL_STAT_RAW + 'hbeat.basic\n{\ninterval=%d\n}\n'
    HBEAT_APP_RAW    = XPL_STAT_RAW + 'hbeat.app\n{\ninterval=%d\nremote-ip=%s\nport=%d\n}\n'
    HBEAT_APPVER_RAW = XPL_STAT_RAW + 'hbeat.app\n{\ninterval=%d\nremote-ip=%s\nport=%d\nversion=%s\n}\n'
    HBEAT_END_RAW    = XPL_STAT_RAW + 'hbeat.end\n{\ninterval=%d\nremote-ip=%s\nport=%d\n}\n'
    HBEAT_REQ_RAW    = XPL_CMND_RAW + 'hbeat.request\n{\ncommand=request\n}\n'

    CONFIG_BASIC_RAW    = XPL_STAT_RAW + 'config.basic\n{\ninterval=%d\n}\n'
    CONFIG_APP_RAW      = XPL_STAT_RAW + 'config.app\n{\ninterval=%d\nremote-ip=%s\nport=%d\n}\n'
    CONFIG_LIST_RAW     = XPL_STAT_RAW + 'config.list\n{\n%s}\n'
    CONFIG_CURRENT_RAW  = XPL_STAT_RAW + 'config.current\n{\n%s}\n'

    def __init__(self, max_line_length=-1, split_char=',', *args, **kwargs):
        xMessage.__init__(self)

        self._type = 'cmnd'
        
        self.address_format = '%s-%s.%s'
        """Used by xMessage base class to format source and target values"""

        # xPL messages only have a single block
        self._block0 = xMessageBlock()
        self.blocks.append(self._block0)

        self.max_line_length = max_line_length
        self.split_char = split_char

        raw = kwargs.get('raw', '')
        if raw != '':
            if not self._raw_to_message(raw):
                raise xPLMessageError('xPLMessage: Unable to construct xPL message from raw string: %s' % raw)

    def __str__(self):
        return self._message_to_raw()

    def __repr__(self):
        return self._message_to_raw().replace('\n', ' ')

    def __iter__(self):
        return self._block0.__iter__()

    def items(self):
        return self._block0.items()

    def keys(self):
        return self._block0.keys()

    def values(self):
        return self._block0.keys()

    def __getitem__(self, key):
        item = self._block0[key]
        if len(item) > 1:
            return item
        else:
            return item[0]

    def __setitem__(self, key, value):
        return self._block0.__setitem__(key, value)

    def message_type():
        doc = """The message type - One of 'cmnd', 'stat' or 'trig'"""
        
        def fget(self):
            return self._type
            
        def fset(self, value):
            v = str(value).lower()
            mtypes = ['cmnd', 'stat', 'trig']
            if v not in mtypes:
                raise ValueError('message_type must be one of %s' % mtypes.join(', '))
            else:
                self._type = v

        return locals()
        
    message_type = property(**message_type())

    def schema_class():
        doc = """The class if the message's schema e.g. audio"""

        def fget(self):
            return self._block0.schema_class
    
        def fset(self, value):
            v = str(value).lower()
            self._block0.schema_class = v

        return locals()

    schema_class = property(**schema_class())

    def schema_type():
        doc = """The type if the message's schema e.g. basic"""

        def fget(self):
            return self._block0.schema_type
    
        def fset(self, value):
            v = str(value).lower()
            self._block0.schema_type = v

        return locals()

    schema_type = property(**schema_type())

    schema = property(lambda self: self._block0.schema)

    def source():
        def fget(self):
            return self.address_format % (self.source_vendor, self.source_device, self.source_instance)

        return locals()

    source = property(**source())

    def is_valid():
        def fget(self):
            svOk = len(self._source_vendor) > 0 and len(self._source_vendor) <= 8
            sdOk = len(self._source_device) > 0 and len(self._source_device) <= 8
            siOk = len(self._source_instance) > 0 and len(self._source_instance) <= 16
    
            tvOk = len(self._target_vendor) > 0 and len(self._target_vendor) <= 8
            tdOk = len(self._target_device) > 0 and len(self._target_device) <= 8
            tiOk = len(self._target_instance) > 0 and len(self._target_instance) <= 16
    
            scOk = len(self.schema_class) > 0 and len(self.schema_class) <= 8
            stOk = len(self.schema_type) > 0 and len(self.schema_type) <= 8
    
            if svOk and sdOk and siOk \
              and (self._target_is_all or (tvOk and tdOk and tiOk)) \
              and scOk and stOk:
                return True
            else:
                return False

        return locals()

    is_valid = property(**is_valid())

    def raw():
        def fget(self):
            if not self.is_valid:
                raise xPLMessageError('Unable to construct valid raw xPL from supplied fields.')
    
            return self._message_to_raw()
    
        def fset(self, value):
            if not self._raw_to_message(value):
                raise xPLMessageError('Unable to construct valid xPL message from raw string')

        return locals()

    raw = property(**raw())

    def _message_to_raw(self):
        hdr = 'xpl-%s\n{\nhop=1\nsource=%s\ntarget=%s\n}\n' % (self.message_type, self.source, self.target)

        body = '%s.%s\n{\n' % (self.schema_class, self.schema_type)

        for key, value in self._block0.items():
            if isinstance(value, list):
                for item in value:
                    body += self._build_chunk(key, item)
            else:
                body += self._build_chunk(key, value)

        body = body + '}\n'

        return hdr + body

    def _build_chunk(self, key, value):
        value = str(value)
        chunk = ''
        
        # If we specify a max line length attempt to split it up
        # using split_char
        line_length = len(key) + 1 + len(value)
        if self.max_line_length != -1 and line_length > self.max_line_length:
            if value.find(self.split_char) != -1:
                items = value.split(self.split_char)
                line = '%s=' % key
                for value in items:
                    if len(line) + len(value) > self.max_line_length:
                        chunk += '%s\n' % line[:-1]
                        line = '%s=%s%s' % (key, value, self.split_char)
                    else:
                        line = '%s%s%s' % (line, value, self.split_char)
                        
                chunk += '%s\n' % line[:-1]
            else:
                rest_of_line_length = self.max_line_length - (len(key) + 1)
                while len(value) > rest_of_line_length:
                    chunk += '%s=%s\n' % (key, value[:rest_of_line_length])
                    value = value[rest_of_line_length:]
                    
                chunk += '%s=%s\n' % (key, value)    
        else:
            chunk += '%s=%s\n' % (key, value)
            
        return chunk

    def _raw_to_message(self, raw):
        ok = True

        try:
            parser = xMessageParser('xpl')
            parser.parse(raw, self)
        except:
            raise
            ok = False

        return ok

    is_heartbeat = property(lambda self: (self.schema_class == 'hbeat'))
    is_heartbeat_app = property(lambda self: (self.schema_class == 'hbeat') and (self.schema_type == 'app'))
    is_heartbeat_basic = property(lambda self: (self.schema_class == 'hbeat') and (self.schema_type == 'basic'))


class xPLHBeatBasic(xPLMessage):
    def __init__(self, source, interval=5):
        xPLMessage.__init__(self, raw=xPLMessage.HBEAT_BASIC_RAW % (source, interval))


class xPLHBeatApp(xPLMessage):
    def __init__(self, source, address, port, interval=5):
        xPLMessage.__init__(self, raw=xPLMessage.HBEAT_BASIC_RAW % (source, interval, address, port))


class xPLHBeatRequest(xPLMessage):
    def __init__(self, source):
        xPLMessage.__init__(self, raw=xPLMessage.HBEAT_REQ_RAW % source)


class xPLHBeatEnd(xPLMessage):
    def __init__(self, source):
        xPLMessage.__init__(self, raw=xPLMessage.HBEAT_END_RAW % source)


class xPLCommand(xPLMessage):
    def __init__(self, source):
        xPLMessage.__init__(self, raw=xPLMessage.XPL_CMND_RAW % source)


class xPLStatus(xPLMessage):
    def __init__(self, source):
        xPLMessage.__init__(self, raw=xPLMessage.XPL_STAT_RAW % source)


class xPLTrigger(xPLMessage):
    def __init__(self, source):
        xPLMessage.__init__(self, raw=xPLMessage.XPL_TRIG_RAW % source)

