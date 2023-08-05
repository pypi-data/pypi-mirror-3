from trosnoth.model.zone import ZoneState, ZoneDef
from trosnoth.test.helpers import pytest_funcarg__logman

team1 = object()
team2 = object()

class Player(object):
    def __init__(self, team, ghost=False, turret=False, isTagging=False):
        self.team = team
        self.ghost = ghost
        self.turret = turret
        # Is the player within tagging distance?
        self.isTagging = isTagging

class Universe(object):
    zoneWithDef = {}
    teams = (team1, team2)

def add_players_to_teams(zone, team1Num, team2Num):
    for x in range(0, team1Num):
        zone.addPlayer(Player(team1))
    for y in range(0, team2Num):
        zone.addPlayer(Player(team2))

def setup_zone():
    universe = Universe()
    defn = ZoneDef(0, None, 0, 0)
    return ZoneState(universe, defn)


def test_zone_one_team_can_tag(logman):
    zone = setup_zone()
    add_players_to_teams(zone, 1, 2)
    
    assert zone.getTeamsWithEnoughNumbers() == set([team2])

def test_zone_no_teams_can_tag_neutral(logman):
    zone = setup_zone()
    add_players_to_teams(zone, 2, 2)

    assert zone.getTeamsWithEnoughNumbers() == set()

def test_zone_both_teams_can_tag(logman):
    zone = setup_zone()
    add_players_to_teams(zone,4,4)

    assert zone.getTeamsWithEnoughNumbers() == set([team1, team2])

def test_zone_ghost_doesnt_count(logman):
    zone = setup_zone()
    add_players_to_teams(zone,2,3)
    zone.addPlayer(Player(team1, ghost=True))
    
    assert zone.getPlayerCounts() == {team1:2, team2:3}
    assert zone.getTeamsWithEnoughNumbers() == set([team2])

def test_zone_turret_doesnt_count(logman):
    zone = setup_zone()
    add_players_to_teams(zone,2,3)
    zone.addPlayer(Player(team1, turret=True))
    
    assert zone.getPlayerCounts() == {team1:2, team2:3}
    assert zone.getTeamsWithEnoughNumbers() == set([team2])

def test_zone_is_tagged_by_no_one_despite_advantage(logman):
    zone = setup_zone()
    add_players_to_teams(zone,2,3)
    zone.playerIsWithinTaggingDistance = replacement_playerIsWithinTaggingDistance
    result = zone.playerWhoTaggedThisZone()
    assert result is None

def test_zone_is_not_tagged_because_no_advantage(logman):
    zone = setup_zone()
    add_players_to_teams(zone,2,1)
    zone.addPlayer(Player(team2, isTagging=True))
    zone.playerIsWithinTaggingDistance = replacement_playerIsWithinTaggingDistance
    result = zone.playerWhoTaggedThisZone()
    assert result is None

def test_zone_is_tagged_with_advantage(logman):
    zone = setup_zone()
    zone.teamsAbleToTag = replacement_team1_able_to_tag
    p1 = Player(team1, isTagging=True)
    zone.addPlayer(p1)
    zone.playerIsWithinTaggingDistance = replacement_playerIsWithinTaggingDistance
    result = zone.playerWhoTaggedThisZone()
    assert result == (p1, team1)

def test_zone_is_set_to_neutral_two_tags(logman):
    zone = setup_zone()
    zone.teamsAbleToTag = replacement_both_teams_able_to_tag
    p1 = Player(team1, isTagging=True)
    p2 = Player(team2, isTagging=True)
    zone.addPlayer(p1)
    zone.addPlayer(p2)
    zone.playerIsWithinTaggingDistance = replacement_playerIsWithinTaggingDistance
    result = zone.playerWhoTaggedThisZone()
    assert result == (None, None)

def test_zone_is_not_recaptured_by_owner(logman):
    zone = setup_zone()
    zone.orbOwner = team1
    zone.teamsAbleToTag = replacement_both_teams_able_to_tag
    # Player1 can tag it, even though they already own the zone
    p1 = Player(team1, isTagging=True)
    zone.addPlayer(p1)
    zone.playerIsWithinTaggingDistance = replacement_playerIsWithinTaggingDistance
    result = zone.playerWhoTaggedThisZone()
    assert result == None

def test_zone_is_not_captured_if_noone_tagging(logman):
    zone = setup_zone()
    zone.teamsAbleToTag = replacement_both_teams_able_to_tag
    # Player1 can tag it, even though they already own the zone
    p1 = Player(team1, isTagging=False)
    zone.addPlayer(p1)
    p2 = Player(team2, isTagging=False)
    zone.addPlayer(p2)
    zone.playerIsWithinTaggingDistance = replacement_playerIsWithinTaggingDistance
    result = zone.playerWhoTaggedThisZone()
    assert result == None

def replacement_playerIsWithinTaggingDistance(player):
    return player.isTagging

def replacement_team1_able_to_tag():
    return set([team1])

def replacement_both_teams_able_to_tag():
    return set([team1, team2])