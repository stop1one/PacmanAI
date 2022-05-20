# myAgents.py
# ---------------
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

from game import Agent
from searchProblems import PositionSearchProblem

import util
import time
import search

"""
IMPORTANT
`agent` defines which agent you will use. By default, it is set to ClosestDotAgent,
but when you're ready to test your own agent, replace it with MyAgent
"""
def createAgents(num_pacmen, agent='MyAgent'):
    return [eval('MyAgent')(index=i) for i in range(num_pacmen)]

path = []
movingIdx = []
isFood = []

class MyAgent(Agent):
    """
    Implementation of your agent.
    """

    def getAction(self, state):
        """
        Returns the next action the agent will take
        """

        "*** YOUR CODE HERE ***"
        global movingIdx, path
        
        agentIdx = self.index
        food = state.getFood()
        problem = AnyFoodSearchProblem(state, agentIdx)

        if agentIdx >= 10: return search.bfs(problem)[0]

        areaIndex = agentIdx%4
        areaRange = [[(0, food.width//2),  (0, food.height//2)], [(0, food.width//2),  (food.height//2+1, food.height)], [(food.width//2+1, food.width), (0, food.height//2)], [(food.width//2+1, food.width), (food.height//2+1, food.height)]]
        w, h = areaRange[areaIndex][0], areaRange[areaIndex][1]

        if isFood[areaIndex]: isFood[areaIndex] = self.isFoodInArea(food, w, h)
 
        if isFood[areaIndex]:
            if movingIdx[agentIdx] >= len(path[agentIdx]):
                path[agentIdx] = self.moveToArea(state, w, h)
                movingIdx[agentIdx] = 0
                nextAction = path[agentIdx][movingIdx[agentIdx]]
                movingIdx[agentIdx] += 1
                return nextAction
            else:
                nextAction = path[agentIdx][movingIdx[agentIdx]]
                movingIdx[agentIdx] += 1
                return nextAction

        else: 
            #return search.bfs(problem)[0]
            return self.efficientBFS(state)

    def moveToArea(self, state, w, h):
        problem = AnyFoodSearchProblem(state, self.index)

        #BFS
        fringe = util.Queue()
        current = (problem.getStartState(), [])
        fringe.push(current)
        closed = []
        
        while not fringe.isEmpty():
            node, path = fringe.pop()
            if problem.isGoalState(node) and w[0] <= node[0] <= w[1] and h[0] <= node[1] <= h[1]:
                return path
            if not node in closed:
                closed.append(node)
                for coord, move, cost in problem.getSuccessors(node):
                    fringe.push((coord, path + [move])) 
        return self.efficientBFS(state)

    def isFoodInArea(self, food, w, h):
        for j in range(w[0], w[1]):
            for k in range(h[0], h[1]):
                if food[j][k]: return True
        return False

    # Algorithm : Using bfs path until any agent eat food
    # This algorithm doesn't have to calculate bfs path every execution
    def efficientBFS(self, state):
        global path, movingIdx
        agentIdx = self.index
        problem = AnyFoodSearchProblem(state, agentIdx)

        if movingIdx[agentIdx] >= len(path[agentIdx]):
            path[agentIdx] = search.bfs(problem)
            movingIdx[agentIdx] = 0
            nextAction = path[agentIdx][movingIdx[agentIdx]]
            movingIdx[agentIdx] += 1
            return nextAction
        else:
            nextAction = path[agentIdx][movingIdx[agentIdx]]
            movingIdx[agentIdx] += 1
            return nextAction
        
    def initialize(self):
        """
        Intialize anything you want to here. This function is called
        when the agent is first created. If you don't need to use it, then
        leave it blank
        """

        "*** YOUR CODE HERE"

        global path, movingIdx, isFood
        path = [list() for _ in range(10)]
        movingIdx = [0 for _ in range(10)]
        isFood = [True for _ in range(4)]

        return

        
"""
Put any other SearchProblems or search methods below. You may also import classes/methods in
search.py and searchProblems.py. (ClosestDotAgent as an example below)
"""

class ClosestDotAgent(Agent):

    def findPathToClosestDot(self, gameState):
        """
        Returns a path (a list of actions) to the closest dot, starting from
        gameState.
        """
        # Here are some useful elements of the startState
        startPosition = gameState.getPacmanPosition(self.index)
        food = gameState.getFood()
        walls = gameState.getWalls()
        problem = AnyFoodSearchProblem(gameState, self.index)


        "*** YOUR CODE HERE ***"

        pacmanCurrent = [problem.getStartState(), [], 0]
        visitedPosition = set()
        # visitedPosition.add(problem.getStartState())
        fringe = util.PriorityQueue()
        fringe.push(pacmanCurrent, pacmanCurrent[2])
        while not fringe.isEmpty():
            pacmanCurrent = fringe.pop()
            if pacmanCurrent[0] in visitedPosition:
                continue
            else:
                visitedPosition.add(pacmanCurrent[0])
            if problem.isGoalState(pacmanCurrent[0]):
                return pacmanCurrent[1]
            else:
                pacmanSuccessors = problem.getSuccessors(pacmanCurrent[0])
            Successor = []
            for item in pacmanSuccessors:  # item: [(x,y), 'direction', cost]
                if item[0] not in visitedPosition:
                    pacmanRoute = pacmanCurrent[1].copy()
                    pacmanRoute.append(item[1])
                    sumCost = pacmanCurrent[2]
                    Successor.append([item[0], pacmanRoute, sumCost + item[2]])
            for item in Successor:
                fringe.push(item, item[2])
        return pacmanCurrent[1]

    def getAction(self, state):
        return search.bfs(AnyFoodSearchProblem(state, self.index))[0]
        return self.findPathToClosestDot(state)[0]

class AnyFoodSearchProblem(PositionSearchProblem):
    """
    A search problem for finding a path to any food.

    This search problem is just like the PositionSearchProblem, but has a
    different goal test, which you need to fill in below.  The state space and
    successor function do not need to be changed.

    The class definition above, AnyFoodSearchProblem(PositionSearchProblem),
    inherits the methods of the PositionSearchProblem.

    You can use this search problem to help you fill in the findPathToClosestDot
    method.
    """

    def __init__(self, gameState, agentIndex):
        "Stores information from the gameState.  You don't need to change this."
        # Store the food for later reference
        self.food = gameState.getFood()

        # Store info for the PositionSearchProblem (no need to change this)
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition(agentIndex)
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE

    def isGoalState(self, state):
        """
        The state is Pacman's position. Fill this in with a goal test that will
        complete the problem definition.
        """
        x,y = state
        if self.food[x][y] == True:
            return True
        return False

