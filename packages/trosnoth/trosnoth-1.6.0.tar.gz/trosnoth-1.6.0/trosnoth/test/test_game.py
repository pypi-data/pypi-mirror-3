import os

from mox import IsA

from trosnoth.test.helpers import pytest_funcarg__mock, pytest_funcarg__logman

from trosnoth.model.mapLayout import LayoutDatabase
from trosnoth.game import makeLocalGame
from trosnoth.utils.components import DynamicPlug
from trosnoth.messages import (JoinRequestMsg, JoinSuccessfulMsg, AddPlayerMsg,
        CannotJoinMsg)

def setup_game(mock):
    halfWidth = 2
    height = 1

    app = mock.CreateMockAnything()
    db = LayoutDatabase(app)
    game = makeLocalGame(os.path.basename(__file__), db, halfWidth, height)

    eventPlug = DynamicPlug(mock.CreateMockAnything())
    requestPlug = DynamicPlug(mock.CreateMockAnything())

    game.addAgent(eventPlug, requestPlug)

    return game, eventPlug, requestPlug

def test_successfulJoin(mock, logman):
    game, eventPlug, requestPlug = setup_game(mock)

    # Expected sequence:
    eventPlug._receive(IsA(AddPlayerMsg))
    eventPlug._receive(IsA(JoinSuccessfulMsg))

    mock.ReplayAll()

    # Test sequence:
    requestPlug.send(JoinRequestMsg('\x00', 7, nick='Player1'.encode(),
            bot=False))

    mock.VerifyAll()

def test_setPlayerLimit(mock, logman):
    game, eventPlug, requestPlug = setup_game(mock)

    # Expected sequence:
    eventPlug._receive(IsA(AddPlayerMsg))
    eventPlug._receive(IsA(JoinSuccessfulMsg))

    eventPlug._receive(IsA(AddPlayerMsg))
    eventPlug._receive(IsA(JoinSuccessfulMsg))

    eventPlug._receive(IsA(CannotJoinMsg))

    mock.ReplayAll()

    # Test sequence:
    game.setPlayerLimits(1)

    requestPlug.send(JoinRequestMsg('\x00', 7, nick='Player1'.encode(),
            bot=False))
    requestPlug.send(JoinRequestMsg('\x00', 1, nick='Player2'.encode(),
            bot=False))
    requestPlug.send(JoinRequestMsg('\x00', 2, nick='Player3'.encode(),
            bot=False))

    mock.VerifyAll()

def test_setPlayerLimit_twice(mock, logman):
    game, eventPlug, requestPlug = setup_game(mock)

    # Expected sequence:
    eventPlug._receive(IsA(AddPlayerMsg))
    eventPlug._receive(IsA(JoinSuccessfulMsg))

    eventPlug._receive(IsA(AddPlayerMsg))
    eventPlug._receive(IsA(JoinSuccessfulMsg))

    eventPlug._receive(IsA(CannotJoinMsg))

    eventPlug._receive(IsA(AddPlayerMsg))
    eventPlug._receive(IsA(JoinSuccessfulMsg))

    mock.ReplayAll()

    # Test sequence:
    game.setPlayerLimits(1)

    requestPlug.send(JoinRequestMsg('\x00', 7, nick='Player1'.encode(),
            bot=False))
    requestPlug.send(JoinRequestMsg('\x00', 1, nick='Player2'.encode(),
            bot=False))
    requestPlug.send(JoinRequestMsg('\x00', 2, nick='Player3'.encode(),
            bot=False))

    game.setPlayerLimits(5)
    requestPlug.send(JoinRequestMsg('\x00', 3, nick='Player4'.encode(),
            bot=False))


    mock.VerifyAll()

