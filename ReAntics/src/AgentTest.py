from AI import vargaspu21_schendel21 as ai_agent

winCount = -1
moveCount = -1
utilCount = -1

def testExpandNode():
  agent = ai_agent.AIPlayer(0)
  agent.init2()
  root = ai_agent.Node(None, None, 0, None, True)
  agent.total = 0
  root.setTurn(0)
  agent.expandNode(root)
  testNodeOut(root)
  printTree(root)

def testNodeOut(node):
  if not node.score == 3:
    print("Root score: {}. Test fail.".format(node.score))
    return
  if not len(node.children) == 1:
    print("Root child count invalid: {}. Test fail.".format(len(node.children)))
    return
  node = node.children[0]
  if not node.score == 3:
    print("Child 1 score: {}. Test fail.".format(node.score))
    return
  if not len(node.children) == 1:
    print("Child 1 child count invalid: {}. Test fail.".format(len(node.children)))
    return
  node = node.children[0]
  if not node.score == 3:
    print("Child 2 score: {}. Test fail.".format(node.score))
    return
  if not len(node.children) == 1:
    print("Child 2 child count invalid: {}. Test fail.".format(len(node.children)))
    return
  node = node.children[0]
  if not node.score == 3:
    print("Child 3 score: {}. Test fail.".format(node.score))
    return
  if not len(node.children) == 2:
    print("Child 3 child count invalid: {}. Test fail.".format(len(node.children)))
    return
  node = node.children[0]
  if not node.score == 4:
    print("Child 4,0 score: {}. Test fail.".format(node.score))
    return
  if not len(node.children) == 0:
    print("Child 4,0 child count invalid: {}. Test fail.".format(len(node.children)))
    return
  node = node.parent.children[1]
  if not node.score == 3:
    print("Child 4,1 score: {}. Test fail.".format(node.score))
    return
  if not len(node.children) == 0:
    print("Child 4,1 child count invalid: {}. Test fail.".format(len(node.children)))
    return
  print("Test Pass!")

def printTree(root):
  print("{}: {}: {}".format(root.depth, root.score, "me" if (root.turn ==0) else "opp"))
  for child in root.children:
    printTree(child)

def getWinnerMock():
  global winCount
  winCount += 1
  if not (winCount == 9 or winCount == 15 or winCount == 16):
    return None
  elif winCount == 9 or winCount == 16:
    return 0
  return 1

def listMovesMock():
  global moveCount
  moveCount += 1
  if moveCount == 7:
    return [None]
  elif moveCount == 6:
    return [None, None, None]
  return [None, None]

def utilityMock():
  global utilCount
  utilCount += 1
  if utilCount == 0:
    return 4
  if utilCount == 1:
    return 3
  if utilCount == 2:
    return -2
  if utilCount == 3:
    return 3
  if utilCount == 4:
    return 1

if __name__ == '__main__':
  testExpandNode()
