from deriv_api.in_memory import InMemory

def test_in_memory():
    obj = InMemory()
    assert isinstance(obj, InMemory)
    obj.set_key_value('hello', {'msg_type': 'test_type', 'val': 123})
    assert obj.has_key('hello')
    assert obj.get_key('hello')['val'] == 123
    assert obj.get_by_msg_type('test_type') == obj.get_key('hello')
    assert obj.has_key('no such key') is False
