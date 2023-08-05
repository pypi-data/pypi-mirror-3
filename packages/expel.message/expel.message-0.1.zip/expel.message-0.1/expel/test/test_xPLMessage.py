import os.path
from expel.message.xpl import xPLMessage, xPLTrigger

def test_RawOut():
    msg = xPLTrigger('sffj-astral.astral1')
    assert msg.message_type == 'trig'
    assert msg.hop == '1'
    msg.schema_class = 'dawndusk'
    msg.schema_type = 'basic'
    msg['type'] = 'dawndusk'
    msg['status'] = 'dawn'
    
    assert msg.raw == 'xpl-trig\n{\nhop=1\nsource=sffj-astral.astral1\ntarget=*\n}\ndawndusk.basic\n{\nstatus=dawn\ntype=dawndusk\n}\n'

def test_RawOutwithLength():
    msg = xPLTrigger('sffj-astral.astral1')
    msg.schema_class = 'test'
    msg.schema_type = 'basic'
    msg['wally'] = 'hello,how,are,you,doing,this,is,a,longer,line,than,normal'
    msg.max_line_length = 30
    
    assert msg.raw == 'xpl-trig\n{\nhop=1\nsource=sffj-astral.astral1\ntarget=*\n}\ntest.basic\n{\nwally=hello,how,are,you,doing\nwally=this,is,a,longer,line\nwally=than,normal\n}\n'

def test_RawOutwithLengthInvalidSplitChar():
    msg = xPLTrigger('sffj-astral.astral1')
    msg.schema_class = 'test'
    msg.schema_type = 'basic'
    msg['wally'] = 'hello,how,are,you,doing,this,is,a,longer,line,than,normal'
    msg.split_char = ':'
    msg.max_line_length = 30
    
    assert msg.raw == 'xpl-trig\n{\nhop=1\nsource=sffj-astral.astral1\ntarget=*\n}\ntest.basic\n{\nwally=hello,how,are,you,doing,\nwally=this,is,a,longer,line,th\nwally=an,normal\n}\n'
    
def test_RawIn():
    msg = xPLMessage(raw='xpl-trig\n{\nhop=2\nsource=sffj-astral.astral1\ntarget=*\n}\ndawndusk.basic\n{\nstatus=dawn\ntype=dawndusk\n}\n')
    
    assert msg.message_type == 'trig'
    assert msg.hop == '2'
    assert msg.source_vendor == 'sffj'
    assert msg.source_device == 'astral'
    assert msg.source_instance == 'astral1'
    
    assert msg.target == '*'
    assert msg.target_is_all == True

    assert msg.schema_class == 'dawndusk'
    assert msg.schema_type == 'basic'
    
    assert msg['status'] == 'dawn'
    assert msg['type'] == 'dawndusk'

def test_ConfigCurrent():
    data = 'xpl-stat\n{\nhop=1\nsource=vendor-device.instance\ntarget=*\n}\nconfig.list\n{\nreconf=newconf\noption=city\noption=group[16]\noption=interval\n}\n'
    m = xPLMessage()
    m.raw = data
    assert len(m['option']) == 3

if __name__ == '__main__':
    test_ConfigCurrent()
    test_RawOut()
    test_RawOutwithLength()
    test_RawOutwithLengthInvalidSplitChar()
    test_RawIn()
    
