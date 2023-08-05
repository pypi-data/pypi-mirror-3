from math import pi
import random
from trosnoth.ai import AI
from trosnoth.model.map import MapLayout
from trosnoth.utils.twist import WeakLoopingCall

GRID_SIZE = 128
class InBlockData(object):
    '''
    Records data about navigation within map blocks.
    '''
    def __init__(self):
        self._data = {}

    def addData(self, world, startPos, action, endPos):
        '''
        Should be called when the given action from the given startPos within
        the given world results in the given endPos.
        '''
        startNode, endNode = self.getNodes(world, startPos, endPos)
        startNode.observeTransition(action, endNode)

    def getNodes(self, world, startPos, endPos):
        '''
        Converts the given start and end points to nodes within this database
        and returns the two nodes.
        '''
        blockIndices = i, j = MapLayout.getMapBlockIndices(*startPos)
        blockDef = world.zoneBlocks[i][j].defn
        layout = blockDef.layout
        x = startPos[0] - blockDef.rect.left
        y = startPos[1] - blockDef.rect.top
        startNode = self._getNode(layout, x, y)

        blockIndices2 = MapLayout.getMapBlockIndices(*endPos)
        if blockIndices2 != blockIndices:
            i2, j2 = blockIndices2
            if i2 < i:
                endNode = self._getExitNode(layout, 'l')
            elif i2 > i:
                endNode = self._getExitNode(layout, 'r')
            elif j2 < j:
                endNode = self._getExitNode(layout, 'u')
            else:
                endNode = self._getExitNode(layout, 'd')
        else:
            x = endPos[0] - blockDef.rect.left
            y = endPos[1] - blockDef.rect.top
            endNode = self._getNode(layout, x, y)

        return startNode, endNode

    def _getLayoutAndNode(self, world, pos):
        '''
        Converts the given position to a node.
        '''
        i, j = MapLayout.getMapBlockIndices(*pos)
        blockDef = world.zoneBlocks[i][j].defn
        layout = blockDef.layout
        x = pos[0] - blockDef.rect.left
        y = pos[1] - blockDef.rect.top
        return layout, self._getNode(layout, x, y)

    def _getLayoutData(self, layout):
        try:
            return self._data[layout]
        except KeyError:
            pass

        result = {}
        for direction in ['u', 'd', 'l', 'r']:
            result[direction] = InBlockNode()

        xCount, yCount = self._getLayoutSize(layout)
        for i in xrange(xCount):
            for j in xrange(yCount):
                result[i, j] = InBlockNode()

        def setDefault(action, i2, j2):
            if i2 < 0:
                node = result['l']
            elif i2 >= xCount:
                node = result['r']
            elif j2 < 0:
                node = result['u']
            elif j2 >= yCount:
                node = result['d']
            else:
                node = result[i2, j2]
            result[i, j].observeTransition(action, node)

        for i in xrange(xCount):
            for j in xrange(yCount):
                setDefault('l', i - 1, j)
                setDefault('r', i + 1, j)
                setDefault('j', i, j - 1)
                setDefault('d', i, j + 1)
                setDefault('jl', i - 1, j - 1)
                setDefault('jr', i + 1, j - 1)
                setDefault('dl', i - 1, j + 1)
                setDefault('dr', i + 1, j + 1)

        self._data[layout] = result
        return result

    def _getLayoutSize(self, layout):
        '''
        Returns the number of nodes in each direction within the given layout.
        '''
        if layout.kind in ('top', 'btm'):
            return ((1024-1) // GRID_SIZE + 1, (384-1) // GRID_SIZE + 1)
        return ((512-1) // GRID_SIZE + 1, (384-1) // GRID_SIZE + 1)

    def _getNode(self, layout, x, y):
        '''
        Returns a node corresponding to the given position within the given map
        block layout.
        '''
        i = x // GRID_SIZE
        j = y // GRID_SIZE
        return self._getLayoutData(layout)[i, j]

    def _getExitNode(self, layout, direction):
        '''
        Returns a node corresponding to exiting the give map block layout in the
        given direction. The parameter "direction" may be one of 'l', 'r', 'u'
        or 'd'.
        '''
        return self._getLayoutData(layout)[direction]

    @staticmethod
    def _getLayout(world, (x, y)):
        i, j = MapLayout.getMapBlockIndices(x, y)
        block = world.zoneBlocks[i][j]
        return block.defn.layout

    def getActionTowardsExit(self, world, pos, direction):
        '''
        Returns the action most likely to get a player from its current position
        to the given exit of its map block.
        '''
        layout, node = self._getLayoutAndNode(world, pos)
        target = self._getExitNode(layout, direction)
        steps = runAStar(node, target)
        return steps[0][0]

class InBlockNode(object):
    def __init__(self):
        self.transitions = {}

    def observeTransition(self, action, result):
        actionResults = self.transitions.setdefault(action, {})
        actionResults[action] = actionResults.get(action, 0) + 1

class Goals(object):
    '''
    Represents an ordered set of goals.
    '''
    def __init__(self, goals=None):
        if goals is None:
            goals = []
        self.goals = goals

    def __len__(self):
        return len(self.goals)

    def __getitem__(self, key):
        return self.goals[key]

    def __iter__(self):
        return iter(self.goals)

    def check(self):
        '''
        Should be called periodically if these goals are the ones to be achieved
        now.
        '''
        if len(self.goals) > 0:
            result = self.goals[0].check()
            if result is None:
                self.goals.pop(0)
            else:
                self.goals[0] = result

        if len(self.goals) == 0:
            return None
        elif len(self.goals) == 1:
            return self.goals[0]
        return self

    def reset(self, goals):
        self.goals = goals

class Goal(object):
    '''
    Interface for a goal that the AI is trying to achieve.
    '''
    def check(self):
        '''
        Should be called periodically if this goal is to be achieved by the
        player. Returns None if the goal has been reached, self is the
        goal is in progress, or some other goal if this goal should be replaced
        by that.
        '''

class LifeBasedGoal(Goal):
    def __init__(self, ai):
        self.ai = ai

    def check(self):
        if self.ai.player.dead:
            self.deadCheck()
        else:
            self.aliveCheck()
        return self

    def deadCheck(self):
        '''
        Default behaviour: move to nearest friendly zone and respawn.
        '''
        if self.ai.player.inRespawnableZone():
            self.ai.doAimAt(0, thrust=0)
            if self.ai.player.respawnGauge == 0:
                self.ai.doRespawn()
        else:
            self.ai.aimAtFriendlyZone()


class AimlessWandering(LifeBasedGoal):
    '''
    Wanders around with no goal.
    '''
    def aliveCheck(self):
        if self.ai.player.canShoot():
            self.ai.fireAtNearestEnemy()
        if self.ai.isAtDecisionPoint():
            action = random.choice(['j', 'jl', 'jr', 'd', 'dl', 'dr', 'l', 'r'])
            self.ai.selectAction(action)

class MoveUpwards(LifeBasedGoal):
    '''
    Tries to climb as far upwards as possible.
    '''
    def __init__(self, ai):
        LifeBasedGoal.__init__(ai)

    def aliveCheck(self):
        if self.ai.player.canShoot():
            self.ai.fireAtNearestEnemy()
        if self.ai.isAtDecisionPoint():
            action = self.ai.inBlockData.getActionTowardsExit(self.ai.world,
                    self.ai.player.pos, 'u')
            self.ai.selectAction(action)

class PathFindingAI(AI):
    nick = 'HunterOmega'
    inBlockData = InBlockData()

    def start(self):
        self.lastDecisionPoint = None
        self.lastAction = None
        self.lastPos = None
        self.ignoreObstacle = None

        self.goal = AimlessWandering(self)
        self._loop = WeakLoopingCall(self, 'tick')
        self._loop.start(0.1)

    def disable(self):
        self._loop.stop()

    def tick(self):
        self.goal.check()

    def aimAtFriendlyZone(self):
        zones = [z for z in self.world.zones if z.orbOwner == self.player.team]
        if len(zones) == 0:
            return

        def getZoneDistance(zone):
            x1, y1 = self.player.pos
            x2, y2 = zone.defn.pos
            return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

        bestZone = min(zones, key=getZoneDistance)
        self.doAimAtPoint(bestZone.defn.pos)

    def fireAtNearestEnemy(self):
        #return      # No shooting for now.
        enemies = [p for p in self.world.players if not
                (p.dead or self.player.isFriendsWith(p))]
        if len(enemies) == 0:
            return

        def getPlayerDistance(p):
            x1, y1 = self.player.pos
            x2, y2 = p.pos
            return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

        nearestEnemy = min(enemies, key=getPlayerDistance)
        if getPlayerDistance(nearestEnemy) < 512:
            self.doAimAtPoint(nearestEnemy.pos)
            self.doShoot()

    def selectAction(self, action):
        if self.player.dead:
            return

        if self.lastAction is not None:
            self.inBlockData.addData(self.world, self.lastDecisionPoint,
                    self.lastAction, self.player.pos)

        if 'l' in action:
            self.doAimAt(-pi/2.)
            self.doMoveLeft()
        elif 'r' in action:
            self.doAimAt(pi/2.)
            self.doMoveRight()
        if 'j' in action:
            self.doJump()
        elif 'd' in action:
            self.doDrop()

        self.lastDecisionPoint = self.player.pos
        self.lastAction = action
        self.ignoreObstacle = self.player.attachedObstacle

    def died(self, killerId):
        self.lastDecisionPoint = None
        self.lastAction = None

    def isAtDecisionPoint(self):
        if self.player.dead:
            return False
        if self.player.pos == self.lastPos:
            return True
        self.lastPos = self.player.pos

        if self.player.attachedObstacle is None:
            self.ignoreObstacle = None
            return False
        if self.lastAction not in ('l', 'r'):
            return True

        node1, node2 = self.inBlockData.getNodes(self.world,
                self.lastDecisionPoint, self.player.pos)
        if node1 != node2:
            return True
        return False


def runAStar(start, target):
    '''
    Runs the A* algorithm from the start node to the target node and returns a
    sequence of steps.
    '''
    raise NotImplementedError
