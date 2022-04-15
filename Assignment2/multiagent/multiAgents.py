# multiAgents.py
# --------------
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


from multiprocessing import managers
from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        layout = currentGameState.getWalls()
        maxDist = layout.height + layout.width

        "*** YOUR CODE HERE ***"
        GhostDists = [manhattanDistance(newPos, gState.getPosition()) for gState in newGhostStates if gState.scaredTimer == 0]
        minGhostDist = min(GhostDists+[maxDist])
        #if minGhostDist == 0: return float("-inf")
        
        if newFood[newPos[0]][newPos[1]]:
            minFoodDist = 0
        else:
            foodDists = [manhattanDistance(newPos, fPos) for fPos in newFood.asList()]
            minFoodDist = min(foodDists, default=0)

        ghostCost = -2 / (minGhostDist + 1)
        foodCost = 1 / (minFoodDist + 1)

        return successorGameState.getScore() + ghostCost + foodCost

def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        actions = gameState.getLegalActions()
        idx = self.minimaxScore(gameState, 0, self.depth)[1]
        return Directions.STOP if idx == -1 else actions[idx]

    def minimaxScore(self, gameState, agentIndex, depth):
        if depth == 0 or gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState), -1
        nextActions = gameState.getLegalActions(agentIndex)
        successorStates = [gameState.generateSuccessor(agentIndex, nextAction) for nextAction in nextActions]
        if agentIndex == 0:
            scores = [self.minimaxScore(successorState, 1, depth)[0] for successorState in successorStates]
            score = max(scores)
        else:
            if agentIndex == gameState.getNumAgents() - 1:
                scores = [self.minimaxScore(successorState, 0, depth-1)[0] for successorState in successorStates]
            else:
                scores = [self.minimaxScore(successorState, agentIndex+1, depth)[0] for successorState in successorStates]
            score = min(scores)
        return score, self.findIndexToScore(score, scores)
    
    def findIndexToScore(self, key, scores):
        for idx in range(len(scores)):
            if key == scores[idx]: return idx
        return 0

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        alpha = float("-inf")
        beta = float("inf")
        return self.AlphaBetaFunc(gameState, self.depth, alpha, beta)[1]

    def AlphaBetaFunc(self, gameState, depth, a, b, agentIndex=0):
        if depth == 0 or gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState), -1
        
        if agentIndex == 0:
            return self.maxScore(gameState, depth, a, b)
        else:
            return self.minScore(gameState, depth, a, b, agentIndex)

    def maxScore(self, gameState, depth, a, b, agentIndex=0):
        v = float("-inf")
        succActions = gameState.getLegalActions(agentIndex)
        nextAction = Directions.STOP
        for action in succActions:
            successorState = gameState.generateSuccessor(agentIndex, action)
            preMax = max(v, self.AlphaBetaFunc(successorState, depth, a, b, agentIndex+1)[0])
            if preMax > b: 
                return preMax, action
            if preMax > v:
                v, nextAction = preMax, action
                a = max(a, v)
        return v, nextAction
    
    def minScore(self, gameState, depth, a, b, agentIndex):
        v = float("inf")
        succActions = gameState.getLegalActions(agentIndex)
        if agentIndex == gameState.getNumAgents()-1:
            nextAgentIndex, nextDepth = 0, depth-1
        else:
            nextAgentIndex, nextDepth = agentIndex + 1, depth
        nextAction = Directions.STOP
        for action in succActions:
            successorState = gameState.generateSuccessor(agentIndex, action)
            preMin = min(v, self.AlphaBetaFunc(successorState, nextDepth, a, b, nextAgentIndex)[0])
            if preMin < a: return preMin, action
            if preMin < v:
                v, nextAction = preMin, action
                b = min(b, v)
        return v, nextAction

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction
