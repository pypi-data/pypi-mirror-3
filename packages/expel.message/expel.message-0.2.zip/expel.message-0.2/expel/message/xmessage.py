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

__all__ = ['xMessage', 'xMessageBlock']

class xMessage(object):
    def __init__(self):
        self._version = ''
        self._hop = 1
        self._source_vendor = ''
        self._source_device = ''
        self._source_instance = ''
        self._target_vendor = ''
        self._target_device = ''
        self._target_instance = ''
        self._target_is_all = True
        self._blocks = []
        self._is_received = False
        self._is_sent = False

    def version():
        def fget(self):
            return self._version

        def fset(self, value):
            self._version = value
            
        return locals()

    version = property(**version())

    def hop():
        def fget(self):
            return self._hop
    
        def fset(self, value):
            self._hop = value
            
        return locals()

    hop = property(**hop())

    def source_vendor():
        def fget(self):
            return self._source_vendor
    
        def fset(self, value):
            v = str(value).lower()
            result = _check_string(v, 1, 8, False)
            if result != '':
                raise ValueError(result)
            else:
                self._source_vendor = v

        return locals()

    source_vendor = property(**source_vendor())

    def source_device():
        def fget(self):
            return self._source_device
    
        def fset(self, value):
            v = str(value).lower()
            result = _check_string(v, 1, 8, False)
            if result != '':
                raise ValueError(result)
            else:
                self._source_device = v

        return locals()

    source_device = property(**source_device())

    def source_instance():
        def fget(self):
            return self._source_instance
    
        def fset(self, value):
            v = str(value).lower()
            result = _check_string(v, 1, 16, False)
            if result != '':
                raise ValueError(result)
            else:
                self._source_instance = v

        return locals()

    source_instance = property(**source_instance())

    def set_source(self, vendor, device='*', instance='*'):
        self.source_vendor = vendor
        self.source_device = device
        self.source_instance = instance

    def target_vendor():
        def fget(self):
            return self._target_vendor
    
        def fset(self, value):
            v = str(value).lower()
            result = _check_string(v, 1, 8, False)
            if result != '':
                raise ValueError(result)
            else:
                self._target_vendor = v
                if v == '*' and self._target_device == '*' and self._target_instance == '*':
                    self._target_is_all = True
                else:
                    self._target_is_all = False

        return locals()

    target_vendor = property(**target_vendor())

    def target_device():
        def fget(self):
            return self._target_device
    
        def fset(self, value):
            v = str(value).lower()
            result = _check_string(v, 1, 8, False)
            if result != '':
                raise ValueError(result)
            else:
                self._target_device = v
                if v == '*' and self._target_vendor == '*' and self._target_instance == '*':
                    self._target_is_all = True
                else:
                    self._target_is_all = False

        return locals()

    target_device = property(**target_device())

    def target_instance():
        def fget(self):
            return self._target_instance
    
        def fset(self, value):
            v = str(value).lower()
            result = _check_string(v, 1, 16, False)
            if result != '':
                raise ValueError(result)
            else:
                self._target_instance = v
                if v == '*' and self._target_vendor == '*' and self._target_device == '*':
                    self._target_is_all = True
                else:
                    self._target_is_all = False

        return locals()

    target_instance = property(**target_instance())

    def set_target(self, vendor, device='*', instance='*'):
        if vendor == '*' and device == '*' and instance == '*':
            self.target_is_all = True
        else:
            self.target_vendor = vendor
            self.target_device = device
            self.target_instance = instance

    def target():
        def fget(self):
            if self._target_is_all:
                return '*'
            else:
                return self.address_format % (self.target_vendor, self.target_device, self.target_instance)

        return locals()

    target = property(**target())

    def target_is_all():
        def fget(self):
            return self._target_is_all
    
        def fset(self, value):
            if value:
                self._target_vendor = '*'
                self._target_device = '*'
                self._target_instance = '*'
    
            self._target_is_all = value

        return locals()

    target_is_all = property(**target_is_all())

    def add_block(self):
        block = xMessageBlock()
        self._blocks.append(block)
        return block

    blocks = property(lambda self: self._blocks)

    def is_received():
        def fget(self):
            return self._is_received
        
        def fset(self, value):
            self._is_received = bool(value)
            
        return locals()

    is_received = property(**is_received())

    def is_sent():
        def fget(self):
            return self._is_sent
        
        def fset(self, value):
            self._is_sent = bool(value)
            
        return locals()

    is_sent = property(**is_sent())


class xMessageBlock(object):
    def __init__(self):
        self._schema_class = ''
        self._schema_type = ''
        self._data = {}

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        if isinstance(value, list):
            self._data[key] = value
        else:
            self._data[key] = [value]

    def get(self, key, default):
        return self._data.get(key, default)

    def scalar(self, key):
        return ','.join(self._data[key])

    def items(self):
        return self._data.items()
        
    def keys(self):
        return self._data.keys()
        
    def values(self):
        return self._data.values()
        
    def __iter__(self):
        return self._data.__iter__()

    def clear(self):
        del self._data[:]

    def schema_class():
        def fget(self):
            return self._schema_class
    
        def fset(self, value):
            v = str(value)
            result = _check_string(v, 1, 8, True)
            if result != '':
                raise ValueError(result)
            else:
                self._schema_class = v

        return locals()

    schema_class = property(**schema_class())

    def schema_type():
        def fget(self):
            return self._schema_type
    
        def fset(self, value):
            v = str(value)
            result = _check_string(v, 1, 8, True)
            if result != '':
                raise ValueError(result)
            else:
                self._schema_type = v

        return locals()

    schema_type = property(**schema_type())

    schema = property(lambda self: '%s.%s' % (self._schema_class, self._schema_type))

def _check_string(theString, minLen, maxLen, lower):
    theString = str(theString)

    if len(theString) < minLen or len(theString) > maxLen:
        return '%s - Illegal field length (%d to %d)' % (theString, minLen, maxLen)

    if lower and theString.lower() != theString:
        return '%s - Illegal casing' % theString

    return ''

