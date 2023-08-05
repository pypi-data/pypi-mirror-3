from expel.message.xmessage import xMessage, xMessageBlock

def testXMessageBlock():
    block = xMessageBlock()
    
    block['name'] = 'test'
    assert block['name'] == ['test']
    
    block['multi'] = 'item1'
    block['multi'].append('item2')
    assert block['multi'] == ['item1', 'item2']

    block['multi'] = ['item1']
    block['multi'].append('item2')
    assert block['multi'] == ['item1', 'item2']

    assert block.scalar('multi') == 'item1,item2'

    block['multi'] = ['item1', 'item2']
    assert block['multi'] == ['item1', 'item2']

    block.schema_class = 'wally'
    assert block.schema_class == 'wally'
    
    block.schema_type = 'basic'
    assert block.schema_type == 'basic'
    
    assert block.schema == 'wally.basic'

def testxMessage():
    msg = xMessage()
    
    assert msg.hop == 1
    assert msg.target_is_all == True
    
    msg.version = '1.99'
    assert msg.version == '1.99'

    msg.source_vendor = 'sffj'
    assert msg.source_vendor == 'sffj'

    msg.source_device = 'clock'
    assert msg.source_device == 'clock'

    msg.source_instance = '00000001'
    assert msg.source_instance == '00000001'

    msg.target_vendor = 'sffj'
    assert msg.target_vendor == 'sffj'

    msg.target_device = 'hub'
    assert msg.target_device == 'hub'

    msg.target_instance = 'domain1'
    assert msg.target_instance == 'domain1'

