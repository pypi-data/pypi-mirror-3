from trosnoth.model.universe import Universe
from trosnoth.model.gameController import GameController
from trosnoth.messages import GameStartMsg, ChangeTimeLimitMsg
from trosnoth.test.helpers import pytest_funcarg__mock, sendMessage

def test_game_controller_change_time_limit(mock):
    layoutDatabase = None
    controller = GameController(layoutDatabase, Universe())
    mock.StubOutWithMock(controller, 'eventPlug')
    mock.ReplayAll()

    sendMessage(controller.orderPlug, GameStartMsg(8000))
    assert controller.getTimeLeft() == 8000

    sendMessage(controller.orderPlug, ChangeTimeLimitMsg(15))
    assert controller.getTimeLeft() == 15

    mock.VerifyAll()