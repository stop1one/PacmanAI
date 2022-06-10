# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DefensiveReflexAgent', second = 'OffensiveReflexAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class MyReflexAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''

    self.start = gameState.getAgentPosition(self.index)



  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
      """
      Finds the next successor which is a grid position (location tuple).
      """
      successor = gameState.generateSuccessor(self.index, action)
      pos = successor.getAgentState(self.index).getPosition()
      if pos != util.nearestPoint(pos):
        # Only half a grid position was covered
        return successor.generateSuccessor(self.index, action)
      else:
        return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}


class OffensiveReflexAgent(MyReflexAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def getFeatures(self, gameState, action):
    features = util.Counter()

    successor = self.getSuccessor(gameState, action)

    foodList = self.getFood(successor).asList()    
    features['successorScore'] = -len(foodList)#self.getScore(successor
    
    if len(foodList) > 0: # This should always be True,  but better safe than sorry

      # Compute distance to my team area
      layout = gameState.data.layout
      w = layout.width
      h = layout.height
      d = -1 if self.red else 0
      myState = successor.getAgentState(self.index)
      myPos = myState.getPosition()
      teamEntry = [(w//2+d, y) for y in range(1, h) if not layout.isWall((w//2+d, y))]
      minTeamDist = min([self.getMazeDistance(myPos, t) for t in teamEntry])
      features['distanceToTeam'] = minTeamDist

      # # Compute distance to the nearest food
      # minFoodDist = min([self.getMazeDistance(myPos, food) for food in foodList])
      # features['distanceToFood'] = minFoodDist
      
      # define
      opponents = [successor.getAgentState(i) for i in self.getOpponents(successor)]
      enemies = [a for a in opponents if not a.isPacman and a.getPosition() != None]

      # evaluate which the food is safe or not
      safeFood = []
      for food in foodList:
        myDist = self.getMazeDistance(myPos, food)
        enemyDist = min([self.getMazeDistance(food, o.getPosition()) for o in opponents])
        if myDist < enemyDist+5: safeFood.append(food)

      # Compute distance to the nearest safe food
      if len(safeFood) > 0:
        minFoodDist = min([self.getMazeDistance(myPos, food) for food in safeFood])
      else:
        minFoodDist = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minFoodDist

      # Compute distance to the nearest enemies
      minEnemyDist = min([self.getMazeDistance(myPos, e.getPosition()) for e in enemies])
      if minEnemyDist <= 7:
        if minEnemyDist <= 2:
          features['distanceToEnemies'] = minEnemyDist
        else:
          features['distanceToEnemies'] = minEnemyDist//2
          #features['distanceToEnemies'] = 0
        capsules = [c for c in layout.capsules if ((self.red and not gameState.isRed(c)) or (not self.red and gameState.isRed(c)))]
        if len(capsules) > 0:
          minCapsuleDist = min([self.getMazeDistance(myPos, c) for c in capsules])
          if minCapsuleDist <= 10:
            features['distanceToCapsule'] = minCapsuleDist
        
      else: features['distanceToEnemies'] = 0
      
      if myState.scaredTimer > 0:
        features['distanceToEnmies'] = 0

    if action == Directions.STOP: features['stop'] = 1
    
    return features

  def getWeights(self, gameState, action):
    numHasFood = gameState.getAgentState(self.index).numCarrying
    if numHasFood >= 2:
      return {'successorScore': 100, 'distanceToTeam':-5, 'distanceToFood': -1, 'distanceToEnemies': 10, 'stop':-100, 'distanceToCapsule':-2}
    return {'successorScore': 100, 'distanceToTeam':0, 'distanceToFood': -1, 'distanceToEnemies': 5, 'stop':-10, 'distanceToCapsule':-2}

class DefensiveReflexAgent(MyReflexAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    layout = gameState.data.layout

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)
    else:
      w = layout.width
      h = layout.height
      d = -1 if self.red else 0
      myPos = successor.getAgentState(self.index).getPosition()
      teamEntry = [(w//2+d, y) for y in range(1, h) if not layout.isWall((w//2+d, y))]
      minTeamBorderDist = min([self.getMazeDistance(myPos, t) for t in teamEntry])
      features['distanceToTeamBorder'] = minTeamBorderDist
    
    capsules = layout.capsules
    capsulesToMyDists = [self.getMazeDistance(myPos, c) for c in capsules]
    capsulesToEnemyDists = [[self.getMazeDistance(c, e.getPosition()) for e in enemies] for c in capsules]
    for i in range(len(capsulesToEnemyDists)):
      minCTED = min(capsulesToEnemyDists[i])
      #if (minCTED - capsulesToMyDists[i] <= 5):
      features['RetrunToCapsules'] = capsulesToMyDists[i]

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -20, 'stop': -100, 'reverse': -3, 'distanceToTeamBorder':-1, 'ReturnToCapsules':-10}

