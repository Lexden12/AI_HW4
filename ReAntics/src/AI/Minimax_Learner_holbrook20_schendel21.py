from AIPlayerUtils import *
from GameState import *
from Move import Move
from Ant import UNIT_STATS
from Construction import CONSTR_STATS
from Constants import *
from Player import *
import random
import sys
sys.path.append("..")  # so other modules can be found in parent dir


##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    def __init__(self, inputPlayerId):
        super(AIPlayer, self).__init__(inputPlayerId, "Minimax_Learner")
        self.root = None
        self.prune = True
        self.test = False
        self.population = []
        self.index = 0
        self.fitness = []
        self.fileName = "AI\schendel21_holbrook20_population.txt"
        self.mutationChance = 0.1
        self.mutationRange = 5.0
        self.gameCount = 0 #number of games we have played with this gene
        self.maxGames = 10 #number of games we will play with each gene
        self.gen = 0 #Current generation number
        self.lastState = None #To save the last game state in case we win
        self.initPopulation()

    def init2(self):
      self.test = True
      self.winCount = -1
      self.moveCount = -1
      self.me = 0
      
    def initPopulation(self):
      try:
        f = open(self.fileName.split('/')[1], "r")
        lines = f.readlines()
        print("Reading existing gene file")
        for line in lines:
          tempGene = line.split(",")
          if len(tempGene) != 12:
            raise ValueError
          self.population.append(list(map(float, tempGene)))
        f.close()
      except:
        print("No gene file found... Making random ones")
        for i in range(10):
          tempGene = []
          for j in range(12):
            tempGene.append(random.uniform(-10, 10))
          self.population.append(tempGene)
      for i in range(len(self.population)):
        self.fitness.append(0)

    def matePopulation(self, mom, dad):
       splitIndex = random.randint(0,12)
       childOne, childTwo= [], []
       childOne.extend(mom[slice(splitIndex)])
       childOne.extend(dad[slice(splitIndex, 12)])
       
       childTwo.extend(dad[slice(splitIndex)])
       childTwo.extend(mom[slice(splitIndex, 12)])
       
       for index, weight in enumerate(childOne):
        mutateFlag = random.uniform(0, 1)
        if mutateFlag <= self.mutationChance:
          mutationDegree = random.uniform(-self.mutationRange, self.mutationRange)
          childOne[index] += mutationDegree
       
       for index, weight in enumerate(childTwo):
        mutateFlag = random.uniform(0, 1)
        if mutateFlag <= self.mutationChance:
          mutationDegree = random.uniform(-self.mutationRange, self.mutationRange)
          childOne[index] += mutationDegree
          
       return childOne, childTwo
    
    def nextGeneration(self):
      total = sum(self.fitness)
      newPopulation = []
      for i in range(len(self.population)//2):
        mom = None
        dad = None
        for j in range(2):
          selectedGeneIndex = random.uniform(0, total)
          totalScore = 0
          for index, score in enumerate(self.fitness):
            if totalScore <= selectedGeneIndex and selectedGeneIndex <= (totalScore + score):
              if j == 0:
                mom = self.population[index]
              elif j == 1:
                dad = self.population[index]
              else:
                print("Invalid Index! {}".format(j))
              break
            totalScore += score
        newPopulation.extend(self.matePopulation(mom, dad))
      self.population = newPopulation.copy()
      self.save()
      
    def save(self):
      f = open('schendel21_holbrook20_population.txt', "w")
      for gene in self.population:
        print(gene)
        for j, weight in enumerate(gene):
          f.write(str(weight))
          if j != len(gene) - 1:
            f.write(',')
          else:
            f.write('\n')
      print("Saved generation")
      f.close()
      
    ##
    #getPlacement
    #
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        if currentState.phase == SETUP_PHASE_1:
            return [(3, 1), (7, 1), (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (8, 3), (9, 3)]
        elif currentState.phase == SETUP_PHASE_2:  # stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 7)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]

    ##
    #getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):
        self.lastState = currentState
        self.me = currentState.whoseTurn
        if self.root is None:
          self.root = Node(None, currentState, 0, None, self.test)

          # For loops goes until set depth
          # in this case a depth of 3 
          self.total = 0
          self.movesInTree = {}
          self.expandNode(self.root)
        if not len(self.root.children) == 0:
          maxNode = self.root.children[0]
          maxScore = self.root.children[0].score
          for child in self.root.children:
            #print(child.move)
            #print(child.score)
            if child.score > maxScore:
              maxScore = child.score
              maxNode = child
          if maxNode.move.moveType == END or self.root.children == []:
            self.root = None
          else:
            self.root = maxNode
          return maxNode.move
        self.root = None
        return Move(END)

    def legalMove(self, state, move):
      if move.coordList is not None and move.moveType == MOVE_ANT:
        if getAntAt(state, move.coordList[0]).hasMoved:
          return False
      return True
        
    ##
    # expandNode
    #
    # takes in a node and recursively expands it by
    # taking all valid moves from that state
    # and creating new nodes for each new move
    # Also implements alpha-beta pruning by using
    # the MiniMax algorithm
    # Further reduces node count by removing duplicate
    # states. (n choose r, not n permute r)
    #
    # returns nothing, just modifies builds out the tree from root
    ##
    def expandNode(self, node):
      win = None
      if not self.test:
        win = getWinner(node.state)
      else:
        win = getWinnerMock()
      if win is not None:
        node.score = 100 if (win == 1) else -100
        node.score = node.score if (node.turn == self.me) else -node.score
        if node.parent is not None:
          node.parent.updateBounds(node, self.me)
        return
      if node.depth == 3:
        if not self.test:
          node.score = self.utility(node.state, self.population[self.index])
        else:
          node.score = utilityMock()
        if node.parent is not None:
          node.parent.updateBounds(node, self.me)
        return
      if not self.test:
        moves = listAllLegalMoves(node.state)
      else:
        moves = listMovesMock()
      for move in moves:
        duplicateCheckList = []
        duplicateCheckList.append(str(move))
        duplicateNode = node
        while duplicateNode.parent is not None:
          duplicateCheckList.append(str(duplicateNode.move))
          duplicateNode = duplicateNode.parent
        duplicateSet = frozenset(duplicateCheckList)
        if hash(duplicateSet) in self.movesInTree:
          continue
        self.movesInTree[hash(duplicateSet)] = duplicateSet
        if not self.test:
          nextState = getNextStateAdversarial(node.state, move)
        else:
          nextState = None
        if node.depth > 0 and node.move.moveType == BUILD and not move.moveType == END:
          continue
        newDepth = node.depth + 1
        newNode = Node(move, nextState, newDepth, node, self.test)
        if self.test and newDepth % 2 == 0:
          newNode.setTurn(0)
        if self.test and not newDepth % 2 == 0:
          newNode.setTurn(1)
        node.addChild(newNode)
        self.expandNode(newNode)
        if self.prune and node.parent is not None:
          if node.turn == self.me:
            if node.alpha >= node.parent.beta or (node.score is not None and node.score >= node.parent.beta):
              if self.test:
                print("Alpha: {}, {}".format(node.alpha, node.parent.beta))
              node.parent.removeChild(node)
              return
          else:
            if node.beta <= node.parent.alpha or (node.score is not None and node.score <= node.parent.alpha):
              if self.test:
                print("Beta: {}, {}".format(node.beta, node.parent.alpha))
              node.parent.removeChild(node)
              return
      
      self.total += len(node.children)
      if node.turn == self.me:
        node.score = node.alpha
      else:
        node.score = node.beta
      if node.parent is not None:
        node.parent.updateBounds(node, self.me)

    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##

    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    #registerWin
    #
    # This agent doesn't learn
    #
    def registerWin(self, hasWon):
        # Need currentGene and numberOfGames variables
        self.gameCount += 1
        #Evaluate the fitness score of the current gene
        self.fitness[self.index] += self.evaluateFitness(hasWon)
       
        #Judge whether the current gene's fitness has been fully evaluated, if so advance to the next gene
        if(self.gameCount >= self.maxGames):
          self.fitness[self.index] /= self.gameCount
          self.index += 1
          self.gameCount = 0
         
          # If all the genes have been full evaluated, create a new population using the fittest ones and reset the current index to the beginning
          if (self.index > len(self.population) - 1):
            self.gen += 1
            print("Generation {} Fitnesses: {}".format(self.gen, self.fitness))
            self.nextGeneration()
            for i in range(len(self.fitness)):
              self.fitness[i] = 0
            self.index = 0
       

    def evaluateFitness(self, hasWon):
      fitness = 0
      if hasWon:
        fitness += 5
      else:
        fitness -= 5
      #use self.lastState to determine what happened in the game
      me = self.me
      enemy = abs(self.me - 1)
      myInv = getCurrPlayerInventory(self.lastState)
      myFood = myInv.foodCount
      enemyInv = getEnemyInv(self, self.lastState)
      enemyFood = enemyInv.foodCount
      hills = getConstrList(self.lastState, types=(ANTHILL,))
      myHill = hills[1] if (hills[0].coords[1] > 5) else hills[0]
      enemyHill = hills[1] if (myHill is hills[0]) else hills[0]
      myQueen = myInv.getQueen()
      enemyQueen = enemyInv.getQueen()
      #get important values for victory (food diff, health diffs)
      foodDiff = myFood - enemyFood
      qDiff = myQueen.health - enemyQueen.health
      hillDiff = myHill.captureHealth - enemyHill.captureHealth
      fitness += foodDiff
      fitness += qDiff
      fitness += (hillDiff // 0.3)
      return max(fitness + 15, 0) #prevent negative fitnesses(breaks nextGen)
 
    ##
    #heuristicStepsToGoal
    #Description: Gets the expected value of a state
    # Weighs the value of the amount of food and workers and offense
    # each player has and estimates how good of a position each player is in
    # This makes the Max player seek to have no army, but rather, make two
    # workers and gather as much food as possible as quickly as possible.
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #                 This will assumed to be a fast clone of the state
    #                 i.e. the board will not be needed/used
    #   gene         - A clone of the gene (a list of weights) that will be
    #                 used to calculate the score of the current state
    ##
    def utility(self, currentState, gene):
      me = currentState.whoseTurn
      enemy = abs(me - 1)
      myInv = getCurrPlayerInventory(currentState)
      myFood = myInv.foodCount
      enemyInv = getEnemyInv(self, currentState)
      enemyFood = enemyInv.foodCount
      tunnels = getConstrList(currentState, types=(TUNNEL,))
      myTunnel = tunnels[1] if (tunnels[0].coords[1] > 5) else tunnels[0]
      enemyTunnel = tunnels[0] if (myTunnel is tunnels[1]) else tunnels[1]
      hills = getConstrList(currentState, types=(ANTHILL,))
      myHill = hills[1] if (hills[0].coords[1] > 5) else hills[0]
      enemyHill = hills[1] if (myHill is hills[0]) else hills[0]
      myQueen = myInv.getQueen()
      enemyQueen = enemyInv.getQueen()

      foods = getConstrList(currentState, None, (FOOD,))

      myWorkers = getAntList(currentState, me, (WORKER,))
      myOffense = getAntList(currentState, me, (SOLDIER, DRONE))
      enemyWorkers = getAntList(currentState, enemy, (WORKER,))
      enemyOffense = getAntList(currentState, enemy, (SOLDIER, DRONE, R_SOLDIER))

      score = 0
      score += (myFood - enemyFood) * gene[0]#0: difference in food
      score += (myQueen.health - enemyQueen.health) * gene[1]#1: difference in queen health
      score += (myHill.captureHealth - enemyHill.captureHealth) * gene[2]#2: difference in anthill health
      score += gene[4] if len(myWorkers) == 2 else 0#4: on/off based on two workers
      #3: average distance from worker to target
      #10: average distance between workers and queen
      tempScore = 0
      totalDist = 0
      if len(myWorkers) > 0:
        for worker in myWorkers:
          totalDist += approxDist(worker.coords, myQueen.coords)
          if worker.carrying: # if carrying go to hill/tunnel
            tempScore += 2
            distanceToTunnel = approxDist(worker.coords, myTunnel.coords)
            distanceToHill = approxDist(worker.coords, myHill.coords)
            dist = min(distanceToHill, distanceToTunnel)
            if dist <= 3:
              tempScore += 1
          else: # if not carrying go to food
            dist = 100
            for food in foods:
              temp = approxDist(worker.coords, food.coords)
              if temp < dist:
                dist = temp
            if dist <= 3:
              tempScore += 1
        score += tempScore * gene[3]
        score += (totalDist/len(myWorkers)) * gene[10]
      #5: average distance from our offense to enemy queen
      #6: average distance from our offense to the first enemy worker
      #7: average distance from our offense to enemy anthill
      queenDist = 0
      workerDist = 0
      anthillDist = 0
      if len(myOffense) > 0:
        for ant in myOffense:
          queenDist += approxDist(ant.coords, enemyQueen.coords)
          if len(enemyWorkers) > 0:
            workerDist += approxDist(ant.coords, enemyWorkers[0].coords)
          anthillDist += approxDist(ant.coords, enemyHill.coords)
        score += (queenDist/len(myOffense)) * gene[5]
        score += (workerDist/len(myOffense)) * gene[6]
        score += (anthillDist/len(myOffense)) * gene[7]
      #8: average distance from enemy offense to our queen
      #9: average distance from enemy offense to our anthill
      queenDist = 0
      anthillDist = 0
      if len(enemyOffense) > 0:
        for ant in enemyOffense:
          queenDist += approxDist(ant.coords, myQueen.coords)
          anthillDist += approxDist(ant.coords, myHill.coords)
        score += (queenDist/len(enemyOffense)) * gene[8]
        score += (anthillDist/len(enemyOffense)) * gene[9]
        score += approxDist(myQueen.coords, enemyQueen.coords) * gene[11]#11: distance between queens
      
      return score if (me == self.me) else -score

     

##
# Node Class
#
# Defines how our Node is set up to use for searching
#
##
class Node:
  def __init__(self, move, state, depth, parent, test):
    self.move = move
    self.state = state
    self.depth = depth
    self.score = None
    if not test:
      self.turn = state.whoseTurn
    else:
      self.turn = None
    self.alpha = -200
    self.beta = 200#alpha and beta values for minimax
    self.children = []
    self.parent = parent
  
  def init2():
    self.test = True

  def addChild(self, node):
    self.children.append(node)

  def removeChild(self, node):
    self.children.remove(node)
  
  def updateBounds(self, node, me):
    if self.turn == me:#max player
      self.alpha = max(self.alpha, node.score)
        
    else:
      self.beta = min(self.beta, node.score)
    return True

  def setTurn(self, turn):
    self.turn = turn
