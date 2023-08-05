from math import pi
import weakref

from trosnoth.ai import AI
from trosnoth.utils.components import Component, Plug, handler
from trosnoth.messages import UpdatePlayerStateMsg
from trosnoth.utils.twist import WeakLoopingCall

class AIClass(AI):
    nick = 'RangerAI'

    def start(self):
        self._goal = None
        self._action = None
        self._loop = WeakLoopingCall(self, 'tick')
        self._loop.start(0.1)

    def disable(self):
        self._loop.stop()

    def tick(self):
        if self.player.dead:
            if self.player.inRespawnableZone():
                self.doAimAt(0, thrust=0)
                if self.player.respawnGauge == 0:
                    self.doRespawn()
            else:
                self.aimAtFriendlyZone()
        else:
            if self._goal is not None:
                if self._goal.tick():
                    return

            if self._action is None:
                self.doStop()
            else:
                self._action.tick()

    def setAction(self, action):
        if action is None:
            self._action = None
            self.doStop()
        else:
            self._action = ActionState(self, action)
            self._action.begin()

    def setGoal(self, goal):
        if goal is None:
            self._goal = None
        else:
            self._goal = GoalState(self, goal)
            self._goal.begin()

    def actionComplete(self):
        if self._goal:
            self.setAction(self._goal.nextAction())
        else:
            self._action = None

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

    def died(self, killerId):
        self._pauseTimer = None
        self.doStop()
        self.aimAtFriendlyZone()

class ActionState(object):
    def __init__(self, ai, action):
        self.ai = ai
        self.action = action

    def begin(self):
        self.action.begin(self.ai, self)

    def tick(self):
        return self.action.tick(self.ai, self)

class GoalState(ActionState):
    def nextAction(self):
        return self.action.nextAction(self.ai, self)

class Action(object):
    def begin(self, ai, state):
        pass

    def tick(self, ai, state):
        pass

    def checkRightBound(self, ai, state, xTarget):
        if state.travelling:
            if ai.player.pos[0] >= xTarget:
                ai.doStop()
                state.travelling = False
                return True
        return False

    def checkLeftBound(self, ai, state, xTarget):
        if state.travelling:
            if ai.player.pos[0] <= xTarget:
                ai.doStop()
                state.travelling = False
                return True
        return False

class MoveLeft(Action):
    '''
    Moves left until reaching the given point.
    '''

    def __init__(self, xTarget=None):
        self.xTarget = xTarget

    def begin(self, ai, state):
        ai.doAimAt(-pi/2.)
        ai.doMoveLeft()
        state.travelling = True

    def tick(self, ai, state):
        if self.xTarget is not None:
            if self.checkLeftBound(ai, state, self.xTarget):
                ai.actionComplete()

class MoveRight(Action):
    '''
    Moves right until reaching the given point.
    '''

    def __init__(self, xTarget=None):
        self.xTarget = xTarget

    def begin(self, ai, state):
        ai.doAimAt(pi/2.)
        ai.doMoveRight()
        state.travelling = True
        if not ai.player.isOnGround():
            ai.actionComplete()

    def tick(self, ai, state):
        if self.xTarget is not None:
            if self.checkRightBound(ai, state, self.xTarget):
                ai.actionComplete()

class AirbourneAction(Action):
    def checkStopped(self, ai, state):
        if state.startTime == ai.player.universe.getGameTime():
            print 'bah'
            return
        if ai.player.isOnGround() or ai.player.isAttachedToWall():
            state.stopped = True
            ai.actionComplete()
            print ' - completed %r' % (self,)

class DropRight(AirbourneAction):
    '''
    Drop and move to the right.
    '''
    def __init__(self, xTarget=None):
        self.xTarget = xTarget

    def begin(self, ai, state):
        ai.doDrop()
        ai.doAimAt(pi/2.)
        ai.doMoveRight()
        state.stopped = False
        state.travelling = True
        state.startTime = ai.player.universe.getGameTime()

    def tick(self, ai, state):
        if self.xTarget is not None:
            self.checkRightBound(ai, state, self.xTarget)
        if not state.stopped:
            self.checkStopped(ai, state)

class DropLeft(AirbourneAction):
    '''
    Drop and move to the right.
    '''
    def __init__(self, xTarget=None):
        self.xTarget = xTarget

    def begin(self, ai, state):
        ai.doDrop()
        ai.doAimAt(-pi/2.)
        ai.doMoveLeft()
        state.stopped = False
        state.travelling = True
        state.startTime = ai.player.universe.getGameTime()

    def tick(self, ai, state):
        if self.xTarget is not None:
            self.checkLeftBound(ai, state, self.xTarget)
        if not state.stopped:
            self.checkStopped(ai, state)

class Drop(AirbourneAction):
    '''
    Drop directly down.
    '''

    def begin(self, ai, state):
        ai.doDrop()
        state.stopped = False
        state.startTime = ai.player.universe.getGameTime()

    def tick(self, ai, state):
        if not state.stopped:
            self.checkStopped(ai, state)

class JumpAction(AirbourneAction):
    def tickThrust(self, ai, state):
        if state.thrusting:
            thrust = 1 - ((ai.player._jumpTime + 0.) /
                    ai.player.universe.physics.playerMaxJumpTime)
            if thrust >= self.thrust:
                ai.doStopJump()
                state.thrusting = False

class JumpRight(JumpAction):
    def __init__(self, thrust, xTarget):
        self.thrust = thrust
        self.xTarget = xTarget

    def begin(self, ai, state):
        ai.doJump()
        ai.doAimAt(pi/2.)
        ai.doMoveRight()
        state.thrusting = True
        state.travelling = True
        state.stopped = False
        state.startTime = ai.player.universe.getGameTime()

    def tick(self, ai, state):
        self.checkStopped(ai, state)
        if state.stopped:
            return

        self.tickThrust(ai, state)
        if state.travelling:
            if ai.player.pos[0] >= self.xTarget:
                ai.doStop()
                state.travelling = False

class JumpLeft(JumpAction):
    def __init__(self, thrust, xTarget):
        self.thrust = thrust
        self.xTarget = xTarget

    def begin(self, ai, state):
        ai.doJump()
        ai.doAimAt(-pi/2.)
        ai.doMoveLeft()
        state.thrusting = True
        state.travelling = True
        state.stopped = False
        state.startTime = ai.player.universe.getGameTime()

    def tick(self, ai, state):
        self.checkStopped(ai, state)
        if state.stopped:
            return

        self.tickThrust(ai, state)
        if state.travelling:
            if ai.player.pos[0] <= self.xTarget:
                ai.doStop()
                state.travelling = False

class VerticalJump(JumpAction):
    def __init__(self, thrust):
        self.thrust = thrust

    def begin(self, ai, state):
        ai.doStop()
        ai.doJump()
        state.thrusting = True
        state.stopped = False
        state.startTime = ai.player.universe.getGameTime()

    def tick(self, ai, state):
        self.checkStopped(ai, state)
        if state.stopped:
            return

        self.tickThrust(ai, state)

class ChimneyJumpRight(JumpAction):
    '''
    Jumps straight up and potentially then moves right as if trying to grab a
    wall.
    '''

    def __init__(self, thrust, yTarget, xTarget=None):
        self.thrust = thrust
        self.yTarget = yTarget
        self.xTarget = xTarget

    def begin(self, ai, state):
        ai.doStop()
        ai.doJump()
        state.travelState = 'stopped'
        state.thrusting = True
        state.stopped = False
        state.startTime = ai.player.universe.getGameTime()

    def tick(self, ai, state):
        self.checkStopped(ai, state)
        if state.stopped:
            return

        self.tickThrust(ai, state)
        if state.travelState == 'stopped':
            if ai.player.pos[1] <= self.yTarget or ai.player.yVel > 0:
                ai.doAimAt(pi/2.)
                ai.doMoveRight()
                state.travelState = 'moving'
        if self.xTarget and state.travelState == 'moving':
            if ai.player.pos[0] >= self.xTarget:
                ai.doStop()
                state.travelState = 'done'

class ChimneyJumpLeft(JumpAction):
    '''
    Jumps straight up and potentially then moves right as if trying to grab a
    wall.
    '''

    def __init__(self, thrust, yTarget, xTarget=None):
        self.thrust = thrust
        self.yTarget = yTarget
        self.xTarget = xTarget

    def begin(self, ai, state):
        ai.doStop()
        ai.doJump()
        state.travelState = 'stopped'
        state.thrusting = True
        state.stopped = False
        state.startTime = ai.player.universe.getGameTime()

    def tick(self, ai, state):
        self.checkStopped(ai, state)
        if state.stopped:
            return

        self.tickThrust(ai, state)
        if state.travelState == 'stopped':
            if ai.player.pos[1] <= self.yTarget or ai.player.yVel > 0:
                ai.doAimAt(-pi/2.)
                ai.doMoveLeft()
                state.travelState = 'moving'
        if self.xTarget and state.travelState == 'moving':
            if ai.player.pos[0] <= self.xTarget:
                ai.doStop()
                state.travelState = 'done'

class ActionRecorder(object):
    '''
    Records the actions taken by a given player.
    '''
    def __init__(self):
        self._loop = WeakLoopingCall(self, 'tick')
        self._constructors = set()

    def recordUI(self, app):
        plug = app.gi.controller
        player = app.gi.detailsInterface.player
        return self.begin(player, plug)

    def begin(self, player, msgPlug):
        constructor = ActionSetConstructor(player, msgPlug)
        constructor.actionSet = actionSet = ActionSet()
        actionSet.stop = lambda: self.stop(constructor)
        self._constructors.add(constructor)

        if not self._loop.running:
            self._loop.start(0.05)

        return actionSet

    def stop(self, constructor):
        self._constructors.remove(constructor)
        constructor.done()
        if len(self._constructors) == 0:
            self._loop.stop()

    def tick(self):
        for constructor in list(self._constructors):
            if constructor.tick():
                self.stop(constructor)

recorder = ActionRecorder()

class ActionSetConstructor(Component):
    inPlug = Plug()
    def __init__(self, player, msgPlug):
        self._actionSet = None
        Component.__init__(self)
        self.player = player
        self.curState = 'start'
        self.curStartPos = None
        self.curChimneyHeight = None
        self.curJumpThrust = None
        self.curIndex = getGridIndex(player.pos)
        self.curIndices = set([self.curIndex])
        self.stateChangeGameTime = None

        self.inPlug.connectPlug(msgPlug)

    @property
    def actionSet(self):
        if self._actionSet is None:
            return None
        return self._actionSet()

    @actionSet.setter
    def actionSet(self, value):
        assert self._actionSet is None, 'actionSet can only be set once'
        self._actionSet = weakref.ref(value)

    @inPlug.defaultHandler
    def _ignore(self, msg):
        pass

    @handler(UpdatePlayerStateMsg, inPlug)
    def playerStateChanged(self, msg):
        if msg.playerId != self.player.id:
            return
        if self.player.universe.getGameTime() == self.stateChangeGameTime:
            return
        if self.actionSet is None:
            return

        if self.curState == 'run':
            if msg.stateKey == 'jump' and msg.value:
                self.addRunAction()
                self.startJump()
        elif self.curState == 'wall':
            if msg.stateKey == 'jump' and msg.value:
                self.startJump()
        elif self.curState == 'chimney':
            if (msg.stateKey in ('left', 'right') and
                    (self.player._state['left'] ^ self.player._state['right'])):
                self.curChimneyHeight = self.player.pos[1]
                self.curState = 'jump'
        if (self.curState in ('jump', 'chimney') and msg.stateKey == 'jump' and
                not msg.value and self.curJumpThrust is None):
            self.curJumpThrust = (1 - (self.player._jumpTime + 0.) /
                    self.player.universe.physics.playerMaxJumpTime)

    def tick(self):
        if self.actionSet is None:
            return True
        if self.player.universe.getGameTime() == self.stateChangeGameTime:
            return False
        index = getGridIndex(self.player.pos)
        if self.curIndex != index:
            self.curIndices.add(index)
            self.curIndex = index

        player = self.player
        if self.curState == 'start':
            if player.isAttachedToWall():
                self.newState('wall')
            elif player.isOnGround():
                self.newState('run')
        elif self.curState == 'run':
            if not player.isOnGround():
                self.addRunAction()
                self.newState('drop')
        elif self.curState == 'wall':
            if not player.isAttachedToWall():
                self.newState('drop')
        elif self.curState == 'drop':
            if player.isAttachedToWall():
                self.addDropAction()
                self.newState('wall')
            elif player.isOnGround():
                self.addDropAction()
                self.newState('run')
        elif self.curState in ('jump', 'chimney'):
            if player.isAttachedToWall():
                self.addJumpAction()
                self.newState('wall')
            elif player.isOnGround():
                self.addJumpAction()
                self.newState('run')

        return False

    def startJump(self):
        self.curChimneyHeight = None
        self.curJumpThrust = None
        if self.player._state['left'] ^ self.player._state['right']:
            self.newState('jump')
        else:
            self.newState('chimney')

    def newState(self, state):
        self.curState = state
        self.curStartPos = self.player.pos
        self.stateChangeGameTime = self.player.universe.getGameTime()

    def addRunAction(self):
        startPos = self.curStartPos[0]
        pos = self.player.pos[0]
        if pos < startPos:
            print 'move left'
            action = MoveLeft(pos)
        elif pos > startPos:
            print 'move right'
            action = MoveRight(pos)
        else:
            return

        for index in self.curIndices:
            self.actionSet.addAction(action, index, self.curIndices)
        self.curIndices = set([self.curIndex])

    def addDropAction(self):
        startPos = self.curStartPos[0]
        pos = self.player.pos[0]

        if pos == startPos:
            print 'drop'
            action = Drop()
        elif pos < startPos:
            print 'drop left'
            action = DropLeft(pos)
        else:
            print 'drop right'
            action = DropRight(pos)

        self.addAction(action)

    def addAction(self, action):
        self.actionSet.addAction(action, getGridIndex(self.curStartPos),
                self.curIndices)
        self.curIndices = set([self.curIndex])

    def addJumpAction(self):
        startPos = self.curStartPos[0]
        pos = self.player.pos[0]
        thrust = 1 if self.curJumpThrust is None else self.curJumpThrust

        if self.curState == 'chimney':
            print 'vertical jump', thrust
            action = VerticalJump(thrust)
        elif self.curChimneyHeight is None:
            if pos < startPos:
                print 'jump left', thrust, pos
                action = JumpLeft(thrust, pos)
            else:
                print 'jump right', thrust, pos
                action = JumpRight(thrust, pos)
        elif pos < startPos or self.player.isAttachedToWall() == 'left':
            print 'chimney jump left', thrust, self.curChimneyHeight, pos
            action = ChimneyJumpLeft(thrust, self.curChimneyHeight, pos)
        else:
            print 'chimney jump right', thrust, self.curChimneyHeight, pos
            action = ChimneyJumpRight(thrust, self.curChimneyHeight, pos)

        self.addAction(action)

    def done(self):
        self.inPlug.disconnectAll()
        if self.actionSet is None:
            return

        if self.curState == 'run':
            self.addRunAction()
        elif self.curState == 'drop':
            self.addDropAction()
        elif self.curState in ('jump', 'chimney'):
            self.addJumpAction()

def getGridIndex(pos):
    x, y = pos
    return ((x + 64) // 128, (y + 64) // 128)

class ActionSet(object):
    def __init__(self):
        self._actions = []

    def addAction(self, action, startIndex, okIndices):
        self._actions.append((action, startIndex, okIndices))

    @property
    def actions(self):
        return [a for (a, si, i) in self._actions]

class MapBlockGoal(object):
    def __init__(self, *actionSets):
        self.grid = {}
        for actionSet in actionSets:
            self.applyActionSet(actionSet)

    def applyActionSet(self, actionSet):
        prevIndex = None
        prevActions = None
        for action, startIndex, okIndices in actionSet._actions:
            if startIndex != prevIndex:
                if prevIndex is not None:
                    self.grid[prevIndex] = prevActions
                prevActions = []
                prevIndex = startIndex
            prevActions.append((action, okIndices))
        if prevIndex is not None:
            self.grid[prevIndex] = prevActions

    def begin(self, ai, state):
        ai.setAction(None)
        state.okIndices = set()
        state.actions = []

    def tick(self, ai, state):
        index = getGridIndex(ai.player.pos)
        if index not in state.okIndices or ai._action is None:
            if index in self.grid:
                actions = list(self.grid[index])
                print 'new actions for grid square %r' % (index,)
                state.actions = actions
                print ' >', actions
                action = (self.nextAction(ai, state))
                ai.setAction(action)
            else:
                print 'no known actions for grid square %r' % (index,)
                state.actions = []
                ai.setAction(None)
            return True
        return False

    def nextAction(self, ai, state):
        if not state.actions:
            state.okIndices = set(getGridIndex(ai.player.pos))
            return None
        action, state.okIndices = state.actions.pop(0)
        state.okIndices.add(getGridIndex(ai.player.pos))
        print ' => new action is %r' % (action,)
        return action


class Tester(object):
    def __init__(self, app, ais):
        self.app = app
        self.ai = ais[0].ai
        self.goal = MapBlockGoal()
        self.act = None
        self.ai.setGoal(self.goal)

    def go(self):
        self.act = recorder.recordUI(self.app)

    def stop(self):
        self.act.stop()
        self.goal.applyActionSet(self.act)

    def r(self):
        self.ai.doMoveRight()

    def l(self):
        self.ai.doMoveLeft()

    def on(self):
        self.ai.setGoal(self.goal)

    def off(self):
        self.ai.setGoal(None)
