# bustersAgents.py
# ----------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

from wekaI import Weka
import util
from game import Agent
from game import Directions
from keyboardAgents import KeyboardAgent
import inference
import busters

class NullGraphics:
    "Placeholder for graphics"
    def initialize(self, state, isBlue = False):
        pass
    def update(self, state):
        pass
    def pause(self):
        pass
    def draw(self, state):
        pass
    def updateDistributions(self, dist):
        pass
    def finish(self):
        pass

class KeyboardInference(inference.InferenceModule):
    """
    Basic inference module for use with the keyboard.
    """
    def initializeUniformly(self, gameState):
        "Begin with a uniform distribution over ghost positions."
        self.beliefs = util.Counter()
        for p in self.legalPositions: self.beliefs[p] = 1.0
        self.beliefs.normalize()

    def observe(self, observation, gameState):
        noisyDistance = observation
        emissionModel = busters.getObservationDistribution(noisyDistance)
        pacmanPosition = gameState.getPacmanPosition()
        allPossible = util.Counter()
        for p in self.legalPositions:
            trueDistance = util.manhattanDistance(p, pacmanPosition)
            if emissionModel[trueDistance] > 0:
                allPossible[p] = 1.0
        allPossible.normalize()
        self.beliefs = allPossible

    def elapseTime(self, gameState):
        pass

    def getBeliefDistribution(self):
        return self.beliefs


class BustersAgent:
    "An agent that tracks and displays its beliefs about ghost positions."

    def __init__( self, index = 0, inference = "ExactInference", ghostAgents = None, observeEnable = True, elapseTimeEnable = True):
        inferenceType = util.lookup(inference, globals())
        self.inferenceModules = [inferenceType(a) for a in ghostAgents]
        self.observeEnable = observeEnable
        self.elapseTimeEnable = elapseTimeEnable
        self.weka = Weka()
        self.weka.start_jvm()

    def registerInitialState(self, gameState):
        "Initializes beliefs and inference modules"
        import __main__
        self.display = __main__._display
        for inference in self.inferenceModules:
            inference.initialize(gameState)
        self.ghostBeliefs = [inf.getBeliefDistribution() for inf in self.inferenceModules]
        self.firstMove = True

    def observationFunction(self, gameState):
        "Removes the ghost states from the gameState"
        agents = gameState.data.agentStates
        gameState.data.agentStates = [agents[0]] + [None for i in range(1, len(agents))]
        return gameState

    def getAction(self, gameState):
        "Updates beliefs, then chooses an action based on updated beliefs."
        #for index, inf in enumerate(self.inferenceModules):
        #    if not self.firstMove and self.elapseTimeEnable:
        #        inf.elapseTime(gameState)
        #    self.firstMove = False
        #    if self.observeEnable:
        #        inf.observeState(gameState)
        #    self.ghostBeliefs[index] = inf.getBeliefDistribution()
        #self.display.updateDistributions(self.ghostBeliefs)
        return self.chooseAction(gameState)

    def chooseAction(self, gameState):
        "By default, a BustersAgent just stops.  This should be overridden."
        return Directions.STOP

class BustersKeyboardAgent(BustersAgent, KeyboardAgent):
    "An agent controlled by the keyboard that displays beliefs about ghost positions."

    def __init__(self, index = 0, inference = "KeyboardInference", ghostAgents = None):
        KeyboardAgent.__init__(self, index)
        BustersAgent.__init__(self, index, inference, ghostAgents)

    def getAction(self, gameState):
        return BustersAgent.getAction(self, gameState)

    def chooseAction(self, gameState):
        return KeyboardAgent.getAction(self, gameState)


    def scorefun(self,state):
        return (state.getScore())


    def printLineData(self, state):  ##################################################################################################################################################
        pacmanx, pacmany = state.getPacmanPosition()

        legal_actions_bool = ""
        if "West" in state.getLegalPacmanActions():
            legal_actions_bool += "1, "
        else:
            legal_actions_bool += "0, "
        if "East" in state.getLegalPacmanActions():
            legal_actions_bool += "1, "
        else:
            legal_actions_bool += "0, "
        if "North" in state.getLegalPacmanActions():
            legal_actions_bool += "1, "
        else:
            legal_actions_bool += "0, "
        if "South" in state.getLegalPacmanActions():
            legal_actions_bool += "1"
        else:
            legal_actions_bool += "0"

        aliveG = ""
        for alive in state.getLivingGhosts():
            if alive:
                aliveG = aliveG + str(1) + ", "
            else:
                aliveG = aliveG + str(0) + ", "
        aliveG = aliveG[:-2]

        ghost_dir = ""
        for direction in [state.getGhostDirections().get(i) for i in range(0, state.getNumAgents() - 1)]:
            if direction is "West":
                ghost_dir += "1, 0, 0, 0, 0, "
            elif direction is "Stop":
                ghost_dir += "0, 1, 0, 0, 0, "
            elif direction is "East":
                ghost_dir += "0, 0, 1, 0, 0, "
            elif direction is "North":
                ghost_dir += "0, 0, 0, 1, 0, "
            elif direction is "South":
                ghost_dir += "0, 0, 0, 0, 1, "
        ghost_dir = ghost_dir[:-2]

        ghostdist = ""
        for dist in state.data.ghostDistances:
            if dist is None:
                dist = -1
            ghostdist = ghostdist + str(dist) + ", "
        ghostdist = ghostdist[:-2]

        ghostspos = ""
        for ghost in state.getGhostPositions():
            ghostx, ghosty = ghost
            ghostspos = ghostspos + str(ghostx) + ", " + str(ghosty) + ", "
        ghostspos = ghostspos[:-2]

        s = ", ".join([
            str(pacmanx),
            str(pacmany),
            legal_actions_bool,
            str(state.getNumAgents() - 1),
            aliveG,
            ghostspos,
            ghost_dir,
            ghostdist,
            str(state.getNumFood()),
            str(state.getDistanceNearestFood()),
            str(state.getScore()),
            str(state.data.agentStates[0].getDirection())
        ])

        return s



from distanceCalculator import Distancer
from game import Actions
from game import Directions
import random, sys

'''Random PacMan Agent'''
class RandomPAgent(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)

    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food

    ''' Print the layout'''
    def printGrid(self, gameState):
        table = ""
        ##print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table

    def chooseAction(self, gameState):
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
        move_random = random.randint(0, 3)
        if   ( move_random == 0 ) and Directions.WEST in legal:  move = Directions.WEST
        if   ( move_random == 1 ) and Directions.EAST in legal: move = Directions.EAST
        if   ( move_random == 2 ) and Directions.NORTH in legal:   move = Directions.NORTH
        if   ( move_random == 3 ) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move

class GreedyBustersAgent(BustersAgent):
    "An agent that charges the closest ghost."

    def registerInitialState(self, gameState):
        "Pre-computes the distance between every two points."
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)

    def chooseAction(self, gameState):
        """
        First computes the most likely position of each ghost that has
        not yet been captured, then chooses an action that brings
        Pacman closer to the closest ghost (according to mazeDistance!).

        To find the mazeDistance between any two positions, use:
          self.distancer.getDistance(pos1, pos2)

        To find the successor position of a position after an action:
          successorPosition = Actions.getSuccessor(position, action)

        livingGhostPositionDistributions, defined below, is a list of
        util.Counter objects equal to the position belief
        distributions for each of the ghosts that are still alive.  It
        is defined based on (these are implementation details about
        which you need not be concerned):

          1) gameState.getLivingGhosts(), a list of booleans, one for each
             agent, indicating whether or not the agent is alive.  Note
             that pacman is always agent 0, so the ghosts are agents 1,
             onwards (just as before).

          2) self.ghostBeliefs, the list of belief distributions for each
             of the ghosts (including ghosts that are not alive).  The
             indices into this list should be 1 less than indices into the
             gameState.getLivingGhosts() list.
        """
        pacmanPosition = gameState.getPacmanPosition()
        legal = [a for a in gameState.getLegalPacmanActions()]
        livingGhosts = gameState.getLivingGhosts()
        livingGhostPositionDistributions = \
            [beliefs for i, beliefs in enumerate(self.ghostBeliefs)
             if livingGhosts[i+1]]
        return Directions.EAST


class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

    def __hash__(self):
        return hash(self.position)

    def __str__(self):
        a + b
        a.__add__(b)
        return "Node({})".format(self.position)

def children(parent, position, grid):
    offsets = []
    width, length = len(grid.data), len(grid.data[0])

    for child in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        offi = position[0] + child[0], position[1] + child[1]
        xw, yw = offi
        if width >= xw >= 0 and length >= yw >= 0 and grid[xw][yw] != True:
            offsets.append(Node(parent, offi))


    return offsets


def aStar(start, goal, grid):

    openset = set()
    closedset = set()
    current = Node(None, start)
    openset.add(current)

    while len(openset) > 0:
        current = min(openset, key=lambda v: v.f)
        if current.position == goal:
            path = []
            while current.parent is not None:
                path.append(current)
                current = current.parent
            path.append(current)
            path.reverse()
            return path

        openset.remove(current)
        closedset.add(current)
        for node in children(current, current.position, grid):

            if node in closedset:
                continue

            new_g = current.g + 1
            if node.g > new_g:
                node.g = new_g
                node.parent = current
            else:
                node.g = new_g
                node.h = abs(node.position[0]-goal[0])+abs(node.position[1]-goal[1])
                node.f = node.g + node.h
                openset.add(node)

        #raise ValueError('No path found')


def closest_ghost(gameState):
    dist = gameState.data.ghostDistances
    alive = gameState.getLivingGhosts()[1:]

    closest_ghostt = (-1, -1)
    min_dist = 999999999999

    for i, ghost in enumerate(alive):
        if dist[i] < min_dist and alive[i]:
            min_dist = dist[i]
            closest_ghostt = gameState.getGhostPositions()[i]

    return closest_ghostt


class BasicAgentAA(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        self.countActions = 0

    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food

    ''' Print the layout'''
    def printGrid(self, gameState):
        table = ""
        #print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table

    def printInfo(self, gameState):
        print "---------------- TICK ", self.countActions, " --------------------------" ################################################################################################
        # Dimensiones del mapa
        width, height = gameState.data.layout.width, gameState.data.layout.height
        print "Width: ", width, " Height: ", height
        # Posicion del Pacman
        print "Pacman position: ", gameState.getPacmanPosition()
        # Acciones legales de pacman en la posicion actual
        print "Legal actions: ", gameState.getLegalPacmanActions()
        # Direccion de pacman
        print "Pacman direction: ", gameState.data.agentStates[0].getDirection()
        # Numero de fantasmas
        print "Number of ghosts: ", gameState.getNumAgents() - 1
        # Fantasmas que estan vivos (el indice 0 del array que se devuelve corresponde a pacman y siempre es false)
        print "Living ghosts: ", gameState.getLivingGhosts()
        # Posicion de los fantasmas
        print "Ghosts positions: ", gameState.getGhostPositions()
        # Direciones de los fantasmas
        print "Ghosts directions: ", [gameState.getGhostDirections().get(i) for i in range(0, gameState.getNumAgents() - 1)]
        # Distancia de manhattan a los fantasmas
        print "Ghosts distances: ", gameState.data.ghostDistances
        # Puntos de comida restantes
        print "Pac dots: ", gameState.getNumFood()
        # Distancia de manhattan a la comida mas cercada
        print "Distance nearest pac dots: ", gameState.getDistanceNearestFood()
        # Paredes del mapa
        print "Map:  \n", gameState.getWalls()
        # Puntuacion
        print "Score: ", gameState.getScore()



    def chooseAction(self, gameState):
        self.countActions = self.countActions + 1
        self.printInfo(gameState)
        move = Directions.STOP
        legal = gameState.getLegalActions(0)

        # goal = closest_ghost(gameState)
        # start = gameState.getPacmanPosition()
        # maze = gameState.getWalls()
        #
        # path = aStar(start, goal, maze)
        # path_next = path[1].position
        #
        # next_move = path_next[0]-start[0], path_next[1]-start[1]


        pacmanx, pacmany = gameState.getPacmanPosition()

        legal_actions_bool = ""
        if "West" in gameState.getLegalPacmanActions():
            legal_actions_bool += "1, "
        else:
            legal_actions_bool += "0, "
        if "East" in gameState.getLegalPacmanActions():
            legal_actions_bool += "1, "
        else:
            legal_actions_bool += "0, "
        if "North" in gameState.getLegalPacmanActions():
            legal_actions_bool += "1, "
        else:
            legal_actions_bool += "0, "
        if "South" in gameState.getLegalPacmanActions():
            legal_actions_bool += "1"
        else:
            legal_actions_bool += "0"


        s = ", ".join([
            str(pacmanx),
            str(pacmany),
            legal_actions_bool,
            str(gameState.getNumFood()),
            str(gameState.getDistanceNearestFood()),
            str(gameState.getScore()),
            str(gameState.data.agentStates[0].getDirection())
        ])

        x = [s]
        next_move = self.weka.predict("./ j48_attselkeyboard_cv.model", x, "./ training_keyboard_present_attsel.arff")

        print next_move


        # if next_move == (0, -1):
        #     move = Directions.SOUTH
        # elif next_move == (0, 1):
        #     move = Directions.NORTH
        # elif next_move == (1, 0):
        #     move = Directions.EAST
        # elif next_move == (-1, 0):
        #     move = Directions.WEST
        #
        # return move



    def scorefun(self,state):
        return (state.getScore())


    def printLineData(self, state):  ##################################################################################################################################################
        pacmanx, pacmany = state.getPacmanPosition()

        legal_actions_bool = ""
        if "West" in state.getLegalPacmanActions():
            legal_actions_bool += "1, "
        else:
            legal_actions_bool += "0, "
        if "East" in state.getLegalPacmanActions():
            legal_actions_bool += "1, "
        else:
            legal_actions_bool += "0, "
        if "North" in state.getLegalPacmanActions():
            legal_actions_bool += "1, "
        else:
            legal_actions_bool += "0, "
        if "South" in state.getLegalPacmanActions():
            legal_actions_bool += "1"
        else:
            legal_actions_bool += "0"

        aliveG = ""
        for alive in state.getLivingGhosts():
            if alive:
                aliveG = aliveG + str(1) + ", "
            else:
                aliveG = aliveG + str(0) + ", "
        aliveG = aliveG[:-2]

        ghost_dir = ""
        for direction in [state.getGhostDirections().get(i) for i in range(0, state.getNumAgents() - 1)]:
            if direction is "West":
                ghost_dir += "1, 0, 0, 0, 0, "
            elif direction is "Stop":
                ghost_dir += "0, 1, 0, 0, 0, "
            elif direction is "East":
                ghost_dir += "0, 0, 1, 0, 0, "
            elif direction is "North":
                ghost_dir += "0, 0, 0, 1, 0, "
            elif direction is "South":
                ghost_dir += "0, 0, 0, 0, 1, "
        ghost_dir = ghost_dir[:-2]

        ghostdist = ""
        for dist in state.data.ghostDistances:
            if dist is None:
                dist = -1
            ghostdist = ghostdist + str(dist) + ", "
        ghostdist = ghostdist[:-2]

        ghostspos = ""
        for ghost in state.getGhostPositions():
            ghostx, ghosty = ghost
            ghostspos = ghostspos + str(ghostx) + ", " + str(ghosty) + ", "
        ghostspos = ghostspos[:-2]

        s = ", ".join([
            str(pacmanx),
            str(pacmany),
            legal_actions_bool,
            str(state.getNumAgents() - 1),
            aliveG,
            ghostspos,
            ghost_dir,
            ghostdist,
            str(state.getNumFood()),
            str(state.getDistanceNearestFood()),
            str(state.getScore()),
            str(state.data.agentStates[0].getDirection())
        ])

        return s