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

import pyparsing as pp

class xMessageParser(object):
    def __init__(self, format='xpl'):
        self._format = format

        if self._format == 'xpl':
            self.header_start = (pp.Literal('xpl-') +
                pp.oneOf('cmnd stat trig').setResultsName('msg_type') +
                pp.LineEnd().suppress()).setParseAction(self.handle_header_start)

            self.source_id = pp.Word(pp.alphanums).setResultsName('sv') + pp.Suppress('-') + pp.Word(pp.alphanums).setResultsName('sd') + pp.Suppress('.') + pp.Word('_' + pp.alphanums).setResultsName('si')
            self.target_id = pp.Or([pp.Word(pp.alphanums).setResultsName('tv') + pp.Suppress('-') + pp.Word(pp.alphanums).setResultsName('td') + pp.Suppress('.') + pp.Word('_' + pp.alphanums).setResultsName('ti'), pp.Literal('*').setResultsName('target')])
            self.separator = '='
        else:
            self.header_start = (pp.Literal('xap-header') +
                pp.LineEnd().suppress()).setParseAction(self.handle_header_start)

            self.source_id = pp.Word(pp.alphanums).setResultsName('sv') + pp.Suppress('.') + pp.Word(pp.alphanums).setResultsName('sd') + pp.Suppress('.') + pp.Word(pp.alphanums).setResultsName('si') + pp.Optional(pp.Suppress(':') + pp.Word(pp.alphanums).setResultsName('subaddress'), '')
            self.target_id = pp.Or([pp.Word(pp.alphanums).setResultsName('tv') + pp.Suppress('.') + pp.Word(pp.alphanums).setResultsName('td') + pp.Suppress('.') + pp.Word(pp.alphanums).setResultsName('ti'), pp.Literal('*').setResultsName('target')])
            self.separator = '=!'

        self.version = 'v' + pp.Suppress('=') + pp.Word(pp.nums).setResultsName('version') + pp.LineEnd().suppress()
        self.hop = 'hop' + pp.Suppress('=') + pp.Word(pp.nums).setResultsName('hop') + pp.LineEnd().suppress()
        self.source = 'source' + pp.Suppress('=') + self.source_id + pp.LineEnd().suppress()
        self.target = 'target' + pp.Suppress('=') + self.target_id + pp.LineEnd().suppress()
        self.uid = 'uid' + pp.Suppress('=') + pp.Word(pp.hexnums, max=8) + pp.LineEnd().suppress()
        self.class_ = 'class' + pp.Suppress('=') + pp.Word(pp.alphanums) + '.' + pp.Word(pp.alphanums) + pp.LineEnd().suppress()

        if self._format == 'xpl':
            self.header_body = pp.Each([self.hop, self.source, self.target]).setParseAction(self.handle_header_body)
        else:
            self.header_body = pp.Each([self.version, self.hop, self.class_, self.uid, self.source, self.target]).setParseAction(self.handle_header_body)

        self.block_start = pp.Literal('{').suppress() + pp.LineEnd().suppress()
        self.block_end = pp.Literal('}').suppress() + pp.LineEnd().suppress()

        self.header = self.header_start + self.block_start + self.header_body + self.block_end

        self.block_header = (pp.Word(pp.alphanums).setResultsName('block_class') + \
                             pp.Suppress('.') + \
                             pp.Word(pp.alphanums).setResultsName('block_type') + \
                             pp.LineEnd().suppress()).setParseAction(self.handle_block_header)

        nonequals = "".join( [ c for c in pp.printables if c not in "=" ] ) + " \t"
        self.block_elem = (pp.Word(nonequals).setResultsName('name') + pp.Literal("=").suppress() + pp.restOfLine.setResultsName('value') + pp.LineEnd()).setParseAction(self.handle_block_elem)

        #self.block_elem = (pp.Word('-' + pp.alphanums).setResultsName('name') + pp.Word(self.separator).setResultsName('sep') + \
        #    pp.Optional(pp.Word(' ' + pp.printables), default='').setResultsName('value') + \
        #    pp.LineEnd().suppress()).setParseAction(self.handle_block_elem)

        self.block_elems = pp.OneOrMore(self.block_elem)

        self.block = self.block_header + self.block_start + self.block_elems + self.block_end + pp.Optional(pp.LineEnd().suppress())

        self.blocks = pp.OneOrMore(self.block)

        if self._format == 'xpl':
            self.message = self.header + pp.Optional(self.block)
        else:
            self.message = self.header + pp.Optional(self.blocks)

    def parse(self, raw, msg):
        self._msg = msg
        self.block_number = -1
        try:
            self.message.parseString(raw)
        except Exception, exc:
            print('xMessageParser: Parse error for raw string %s' % raw)
            print exc

    def handle_header_start(self, toks):
        d = toks.asDict()

        if self._format == 'xpl':
            self._msg.message_type = d['msg_type']

    def handle_header_body(self, toks):
        d = toks.asDict()
        self._msg.hop = d['hop']

        self._msg.set_source(d['sv'], d['sd'], d['si'])

        if d.has_key('target'):
            self._msg.set_target(d['target'])
        else:
            self._msg.set_target(d['tv'], d['td'], d['ti'])

    def handle_block_header(self, toks):
        d = toks.asDict()

        self.block_number = self.block_number+ 1

        if len(self._msg.blocks) > self.block_number:
            block = self._msg.blocks[self.block_number]
        else:
            block = self._msg.add_block()

        block.schema_class = str(d['block_class']).lower()
        block.schema_type = str(d['block_type']).lower()

    def handle_block_elem(self, toks):
        d = toks.asDict()

        block = self._msg.blocks[self.block_number]
        
        name = str(d['name']).lower()
        value = str(d['value'])
        
        block[name] = value
