from trosnoth.model.universe import (Universe, DEFAULT_TEAM_NAME_1,
        DEFAULT_TEAM_NAME_2)
from trosnoth.model.voteArbiter import VoteArbiter

class Player(object):
    def __init__(self, **kwargs):
        values = {
            'bot': False,
        }
        values.update(kwargs)
        for k, v in values.iteritems():
            setattr(self, k, v)

def makeUniverse(**kwargs):
    result = object.__new__(Universe)
    for k, v in kwargs.iteritems():
        setattr(result, k, v)
    return result

def makeArbiter(universe):
    plug = object()
    return VoteArbiter(universe, plug, None)

def assertNameAndPlayers(item, name, players):
    iName, iPlayers = item
    assert name == iName
    assert set(iPlayers) == set(players)

def test_getDesiredTeams_noSelection():
    p1 = Player(preferredTeam='')
    p2 = Player(preferredTeam='')
    p3 = Player(preferredTeam='')
    u = makeUniverse(players=[p1, p2, p3])
    arbiter = makeArbiter(u)

    items = arbiter._getDesiredTeams()
    assert len(items) == 1
    assertNameAndPlayers(items[0], '', (p1, p2, p3))

def test_getNewTeams_noSelection():
    p1 = Player(preferredTeam='')
    p2 = Player(preferredTeam='')
    p3 = Player(preferredTeam='')
    u = makeUniverse(players=[p1, p2, p3])
    arbiter = makeArbiter(u)

    teamName1, players1, teamName2, players2 = arbiter._getNewTeams()
    assert teamName1 != teamName2
    assert teamName1 in (DEFAULT_TEAM_NAME_1, DEFAULT_TEAM_NAME_2)
    assert teamName2 in (DEFAULT_TEAM_NAME_1, DEFAULT_TEAM_NAME_2)
    assert len(players1) + len(players2) == len(u.players)
    assert abs(len(players1) - len(players2)) <= 1

def test_getNewTeams_noSelection_2p():
    p1 = Player(preferredTeam='')
    p2 = Player(preferredTeam='')
    u = makeUniverse(players=[p1, p2])
    arbiter = makeArbiter(u)

    teamName1, players1, teamName2, players2 = arbiter._getNewTeams()
    assert teamName1 != teamName2
    assert teamName1 in (DEFAULT_TEAM_NAME_1, DEFAULT_TEAM_NAME_2)
    assert teamName2 in (DEFAULT_TEAM_NAME_1, DEFAULT_TEAM_NAME_2)
    assert len(players1) + len(players2) == len(u.players)
    assert abs(len(players1) - len(players2)) <= 1

def test_getDesiredTeams_oneSelection():
    p1 = Player(preferredTeam='')
    p2 = Player(preferredTeam='')
    p3 = Player(preferredTeam='A')
    u = makeUniverse(players=[p1, p2, p3])
    arbiter = makeArbiter(u)

    items = arbiter._getDesiredTeams()
    print 'items:', items
    assert len(items) == 2
    assertNameAndPlayers(items[0], '', (p1, p2))
    assertNameAndPlayers(items[1], 'A', (p3,))

def test_getDesiredTeams_twoSelections_with_nonSelection():
    p1 = Player(preferredTeam='')
    p2 = Player(preferredTeam='B')
    p3 = Player(preferredTeam='A')
    p4 = Player(preferredTeam='')
    u = makeUniverse(players=[p1, p2, p3, p4])
    arbiter = makeArbiter(u)

    items = arbiter._getDesiredTeams()
    print 'items:', items
    assert len(items) == 3
    assertNameAndPlayers(items[0], '', (p1, p4))
    assertNameAndPlayers(items[1], 'B', (p2,))
    assertNameAndPlayers(items[2], 'A', (p3,))

def assertTeams((teamName1, players1, teamName2, players2), names1, names2):
    '''
    Asserts that the team names are in the allowed team names, and returns
    (players1, players2) in the order that the team names are given to this
    function.
    '''
    assert teamName1 != teamName2

    if not isinstance(names1, tuple): names1 = (names1,)
    if not isinstance(names2, tuple): names2 = (names2,)

    if teamName1 in names1:
        assert teamName2 in names2
        return players1, players2
    elif teamName1 in names2:
        assert teamName2 in names1
        return players2, players1
    raise AssertionError('Unexpected team name: %r' % (teamName1,))

def test_getNewTeams_oneSelection():
    p1 = Player(preferredTeam='')
    p2 = Player(preferredTeam='')
    p3 = Player(preferredTeam='A')
    u = makeUniverse(players=[p1, p2, p3])
    arbiter = makeArbiter(u)

    result = arbiter._getNewTeams()
    playersA, playersB = assertTeams(result, 'A', (DEFAULT_TEAM_NAME_1,
            DEFAULT_TEAM_NAME_2))
    assert p3 in playersA
    assert abs(len(playersA) - len(playersB)) == 1

def test_getDesiredTeams_twoSelections():
    p1 = Player(preferredTeam='B')
    p2 = Player(preferredTeam='A')
    p3 = Player(preferredTeam='A')
    u = makeUniverse(players=[p1, p2, p3])
    arbiter = makeArbiter(u)

    items = arbiter._getDesiredTeams()
    print 'items:', items
    assert len(items) == 2
    assertNameAndPlayers(items[0], 'A', (p3, p2))
    assertNameAndPlayers(items[1], 'B', (p1,))

def test_getNewTeams_twoSelections():
    p1 = Player(preferredTeam='B')
    p2 = Player(preferredTeam='A')
    p3 = Player(preferredTeam='A')
    u = makeUniverse(players=[p1, p2, p3])
    arbiter = makeArbiter(u)

    result = arbiter._getNewTeams()
    playersA, playersB = assertTeams(result, 'A', 'B')
    assert set(playersA) == set([p2, p3])
    assert set(playersB) == set([p1])

def test_getNewTeams_twoSelections_with_nonSelections():
    p1 = Player(preferredTeam='B')
    p2 = Player(preferredTeam='A')
    p3 = Player(preferredTeam='')
    p4 = Player(preferredTeam='')
    p5 = Player(preferredTeam='B')
    p6 = Player(preferredTeam='A')
    p7 = Player(preferredTeam='B')
    p8 = Player(preferredTeam='A')
    p9 = Player(preferredTeam='')
    p10 = Player(preferredTeam='')
    u = makeUniverse(players=[p1, p2, p3, p4, p5, p6, p7, p8, p9, p10])
    arbiter = makeArbiter(u)

    result = arbiter._getNewTeams()
    playersA, playersB = assertTeams(result, 'A', 'B')
    assert p2 in playersA
    assert p6 in playersA
    assert p8 in playersA
    assert p1 in playersB
    assert p5 in playersB
    assert p7 in playersB
    assert len(playersA) == 5
    assert len(playersB) == 5

def test_getDesiredTeams_threeSelections():
    p1 = Player(preferredTeam='B')
    p2 = Player(preferredTeam='C')
    p3 = Player(preferredTeam='A')
    p4 = Player(preferredTeam='C')
    p5 = Player(preferredTeam='A')
    p6 = Player(preferredTeam='A')
    u = makeUniverse(players=[p1, p2, p3, p4, p5, p6])
    arbiter = makeArbiter(u)

    items = arbiter._getDesiredTeams()
    print 'items:', items
    assert len(items) == 3
    assertNameAndPlayers(items[0], 'A', (p3, p6, p5))
    assertNameAndPlayers(items[1], 'C', (p2, p4))
    assertNameAndPlayers(items[2], 'B', (p1,))

def test_getNewTeams_threeSelections():
    p1 = Player(preferredTeam='B')
    p2 = Player(preferredTeam='C')
    p3 = Player(preferredTeam='A')
    p4 = Player(preferredTeam='C')
    p5 = Player(preferredTeam='A')
    p6 = Player(preferredTeam='A')
    u = makeUniverse(players=[p1, p2, p3, p4, p5, p6])
    arbiter = makeArbiter(u)

    result = arbiter._getNewTeams()
    playersA, playersC = assertTeams(result, 'A', 'C')
    assert set(playersA) == set([p3, p5, p6])
    assert set(playersC) == set([p1, p2, p4])

def test_getNewTeams_threeSelections_arbitraryDecision():
    p1 = Player(preferredTeam='C')
    p2 = Player(preferredTeam='C')
    p3 = Player(preferredTeam='A')
    p4 = Player(preferredTeam='C')
    p5 = Player(preferredTeam='A')
    p6 = Player(preferredTeam='A')
    p7 = Player(preferredTeam='B')
    p8 = Player(preferredTeam='B')
    u = makeUniverse(players=[p1, p2, p3, p4, p5, p6, p7, p8])
    arbiter = makeArbiter(u)

    result = arbiter._getNewTeams()
    playersA, playersC = assertTeams(result, 'A', 'C')
    assert len(playersA) == len(playersC) == 4
    for p in (p1, p2, p4):
        assert p in playersC
    for p in (p3, p5, p6):
        assert p in playersA
    assert (p7 in playersA and p8 in playersC) or (p7 in playersC and p8 in
            playersA)

def test_getNewSize_SimpleMajority():
    p1 = Player(preferredSize=(5, 3))
    p2 = Player(preferredSize=(5, 3))
    p3 = Player(preferredSize=(1, 1))
    u = makeUniverse(players=[p1, p2, p3])
    arbiter = makeArbiter(u)

    size = arbiter._getNewSize(None)
    print 'size:', size
    assert size == (5, 3)

def test_getNewSize_ManyVotes():
    p1 = Player(preferredSize=(5, 3))
    p2 = Player(preferredSize=(5, 3))
    p3 = Player(preferredSize=(1, 1))
    p4 = Player(preferredSize=(1, 2))
    p5 = Player(preferredSize=(2, 1))
    u = makeUniverse(players=[p1, p2, p3, p4, p5])
    arbiter = makeArbiter(u)

    size = arbiter._getNewSize(None)
    print 'size:', size
    assert size == (5, 3)

def test_getNewSize_1PDefault():
    p1 = Player(preferredSize=(0, 0))
    u = makeUniverse(players=[p1])
    arbiter = makeArbiter(u)

    size = arbiter._getNewSize(1)
    print 'size:', size
    assert size == (1, 1)

def test_getNewSize_2PDefault():
    p1 = Player(preferredSize=(0, 0))
    u = makeUniverse(players=[p1])
    arbiter = makeArbiter(u)

    size = arbiter._getNewSize(2)
    print 'size:', size
    assert size == (1, 1)

def test_getNewSize_3PDefault():
    p1 = Player(preferredSize=(0, 0))
    u = makeUniverse(players=[p1])
    arbiter = makeArbiter(u)

    size = arbiter._getNewSize(3)
    print 'size:', size
    assert size == (1, 1)

def test_getNewSize_4PDefault():
    p1 = Player(preferredSize=(0, 0))
    u = makeUniverse(players=[p1])
    arbiter = makeArbiter(u)

    size = arbiter._getNewSize(4)
    print 'size:', size
    assert size == (5, 1)

def test_getNewSize_5PDefault():
    p1 = Player(preferredSize=(0, 0))
    u = makeUniverse(players=[p1])
    arbiter = makeArbiter(u)

    size = arbiter._getNewSize(5)
    print 'size:', size
    assert size == (3, 2)

def test_getNewSize_6PDefault():
    p1 = Player(preferredSize=(0, 0))
    u = makeUniverse(players=[p1])
    arbiter = makeArbiter(u)

    size = arbiter._getNewSize(6)
    print 'size:', size
    assert size == (3, 2)

def test_getNewSize_Deadlock():
    p1 = Player(preferredSize=(5, 3))
    p2 = Player(preferredSize=(5, 3))
    p3 = Player(preferredSize=(5, 4))
    p4 = Player(preferredSize=(5, 4))
    p5 = Player(preferredSize=(2, 1))
    u = makeUniverse(players=[p1, p2, p3, p4, p5])
    arbiter = makeArbiter(u)

    size = arbiter._getNewSize(1)
    print 'size:', size
    assert size in [(5, 3), (5, 4)]

def test_getNewSize_DeadlockWithDefault1():
    p1 = Player(preferredSize=(5, 3))
    p2 = Player(preferredSize=(5, 3))
    p3 = Player(preferredSize=(0, 0))
    p4 = Player(preferredSize=(0, 0))
    p5 = Player(preferredSize=(2, 1))
    u = makeUniverse(players=[p1, p2, p3, p4, p5])
    arbiter = makeArbiter(u)

    size = arbiter._getNewSize(1)
    print 'size:', size
    assert size == (1, 1)

def test_getNewSize_DeadlockWithDefault2():
    p1 = Player(preferredSize=(0, 0))
    p2 = Player(preferredSize=(0, 0))
    p3 = Player(preferredSize=(5, 4))
    p4 = Player(preferredSize=(5, 4))
    p5 = Player(preferredSize=(2, 1))
    u = makeUniverse(players=[p1, p2, p3, p4, p5])
    arbiter = makeArbiter(u)

    size = arbiter._getNewSize(1)
    print 'size:', size
    assert size == (1, 1)

def test_getNewDuration_SimpleMajority():
    p1 = Player(preferredDuration=17)
    p2 = Player(preferredDuration=17)
    p3 = Player(preferredDuration=3)
    u = makeUniverse(players=[p1, p2, p3])
    arbiter = makeArbiter(u)

    duration = arbiter._getNewDuration(None)
    assert duration == 17

def test_getNewDuration_ManyVotes():
    p1 = Player(preferredDuration=17)
    p2 = Player(preferredDuration=17)
    p3 = Player(preferredDuration=3)
    p4 = Player(preferredDuration=4)
    p5 = Player(preferredDuration=5)
    u = makeUniverse(players=[p1, p2, p3, p4, p5])
    arbiter = makeArbiter(u)

    duration = arbiter._getNewDuration(None)
    assert duration == 17

def test_getNewDuration_SmallDefault():
    p1 = Player(preferredDuration=0)
    u = makeUniverse(players=[p1])
    arbiter = makeArbiter(u)

    duration = arbiter._getNewDuration((1, 1))
    assert duration == 600

def test_getNewDuration_WideDefault():
    p1 = Player(preferredDuration=0)
    u = makeUniverse(players=[p1])
    arbiter = makeArbiter(u)

    duration = arbiter._getNewDuration((5, 1))
    assert duration == 1200

def test_getNewDuration_StandardDefault():
    p1 = Player(preferredDuration=0)
    u = makeUniverse(players=[p1])
    arbiter = makeArbiter(u)

    duration = arbiter._getNewDuration((3, 2))
    assert duration == 45 * 60

def test_getNewDuration_Deadlock():
    p1 = Player(preferredDuration=18)
    p2 = Player(preferredDuration=18)
    p3 = Player(preferredDuration=110)
    p4 = Player(preferredDuration=110)
    p5 = Player(preferredDuration=7)
    u = makeUniverse(players=[p1, p2, p3, p4, p5])
    arbiter = makeArbiter(u)

    duration = arbiter._getNewDuration((3, 2))
    assert duration in (18, 110)

def test_getNewDuration_DeadlockWithDefault1():
    p1 = Player(preferredDuration=18)
    p2 = Player(preferredDuration=18)
    p3 = Player(preferredDuration=0)
    p4 = Player(preferredDuration=0)
    p5 = Player(preferredDuration=7)
    u = makeUniverse(players=[p1, p2, p3, p4, p5])
    arbiter = makeArbiter(u)

    duration = arbiter._getNewDuration((3, 2))
    assert duration == 45 * 60

def test_getNewDuration_DeadlockWithDefault2():
    p1 = Player(preferredDuration=0)
    p2 = Player(preferredDuration=0)
    p3 = Player(preferredDuration=110)
    p4 = Player(preferredDuration=110)
    p5 = Player(preferredDuration=7)
    u = makeUniverse(players=[p1, p2, p3, p4, p5])
    arbiter = makeArbiter(u)

    duration = arbiter._getNewDuration((3, 2))
    assert duration == 45 * 60

def test_getNewSize_TwoPlayersAgree():
    p1 = Player(preferredSize=(3, 1))
    p2 = Player(preferredSize=(3, 1))
    u = makeUniverse(players=[p1, p2])
    arbiter = makeArbiter(u)

    size = arbiter._getNewSize(1)
    print 'size:', size
    assert size == (3, 1)

def test_getNewSize_TwoPlayersAgree_AI_included():
    p1 = Player(preferredSize=(3, 1), bot=False)
    p2 = Player(preferredSize=(3, 1), bot=False)
    p3 = Player(preferredSize=(0, 0), bot=True)
    p4 = Player(preferredSize=(0, 0), bot=True)
    p5 = Player(preferredSize=(0, 0), bot=True)
    p6 = Player(preferredSize=(0, 0), bot=True)
    u = makeUniverse(players=[p1, p2, p3, p4, p5, p6])
    arbiter = makeArbiter(u)

    size = arbiter._getNewSize(1)
    print 'size:', size
    assert size == (3, 1)

def test_getNewDuration_AI_included():
    p1 = Player(preferredDuration=17, bot=False)
    p2 = Player(preferredDuration=17, bot=False)
    p3 = Player(preferredDuration=0, bot=True)
    p4 = Player(preferredDuration=0, bot=True)
    p5 = Player(preferredDuration=0, bot=True)
    p6 = Player(preferredDuration=0, bot=True)
    u = makeUniverse(players=[p1, p2, p3, p4, p5, p6])
    arbiter = makeArbiter(u)

    duration = arbiter._getNewDuration((1, 1))
    assert duration == 17

def test_getNewTeams_2p_AI_included():
    p1 = Player(preferredTeam='', bot=False)
    p2 = Player(preferredTeam='', bot=False)
    p3 = Player(preferredTeam='', bot=True)
    p4 = Player(preferredTeam='', bot=True)
    p5 = Player(preferredTeam='', bot=True)
    p6 = Player(preferredTeam='', bot=True)
    u = makeUniverse(players=[p1, p2, p3, p4, p5, p6])
    arbiter = makeArbiter(u)

    teamName1, players1, teamName2, players2 = arbiter._getNewTeams()
    assert teamName1 != teamName2
    assert teamName1 in (DEFAULT_TEAM_NAME_1, DEFAULT_TEAM_NAME_2)
    assert teamName2 in (DEFAULT_TEAM_NAME_1, DEFAULT_TEAM_NAME_2)
    assert len(players1) == 1
    assert len(players2) == 1

