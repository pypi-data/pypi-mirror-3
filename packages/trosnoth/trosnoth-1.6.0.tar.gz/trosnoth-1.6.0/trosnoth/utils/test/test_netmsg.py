from trosnoth.utils.netmsg import *

class MyMsg(NetworkMessage):
    fields = 'playerId', 'msgId', 'comment'
    packspec = 'cB*'
    idString='Cust'

def test_simpleMessage():
    a = MyMsg('x', 34, 'ok then')
    assert a.playerId == 'x'
    assert a.msgId == 34
    assert a.comment == 'ok then'

    txt = a.pack()
    assert isinstance(txt, str)

    C = MessageCollection(MyMsg)
    d = C.buildMessage(txt)
    assert d is not a
    assert d.playerId == 'x'
    assert d.msgId == 34
    assert d.comment == 'ok then'

    C2 = MessageCollection()
    try:
        e = C2.buildMessage(txt)
    except MessageTypeError:
        pass
    else:
        assert False, 'Expected exception'
