import time
from random import random

from data.point import Point
from solver import Solver

SOLVER = Solver([[]])


def arrayHash(a) -> int:
    if a is None:
        return 0
    result = 1
    for elem in a:
        result = 31 * result + elem
    return result


def getMillis():
    return int(round(time.time() * 1000))


def getRandom(minVal, maxVal):
    """Helper random method, not directly using randrange (inaccuracies)"""
    return int(random() * (maxVal - minVal + 1) + minVal)


def generateGameBoard(width, height, difficulty):
    """
     * @param width - width of board
     * @param height - height of board
     * @param difficulty - scale from 1 to 10, determines amount of blocks used
     * @return board with a possible solution
     """
    width -= 1
    board = [[0 for _ in range(height)] for _ in range(width + 1)]
    total = width * height
    blocksNeeded = (total / 2 + total * (difficulty - 2) / 20)
    randomPercentage = blocksNeeded / total
    counted = 0
    filledPoints = set()
    for i in range(width):
        for j in range(height):
            if random() < randomPercentage:
                counted += 1
                board[i][j] = 1
                filledPoints.add(Point(i, j))
    needed = int(blocksNeeded - counted)
    if needed < 0:
        for p in filledPoints:
            board[p.getX()][p.getY()] = 0
            needed -= 1
            if needed == 0:
                break
    elif needed > 0:
        while needed != 0:
            x = getRandom(0, width - 1)
            y = getRandom(0, height - 1)
            o = Point(x, y)
            if o not in filledPoints:
                filledPoints.add(o)
                needed -= 1
                board[x][y] = 1
    solver = SOLVER.setBoard(board)
    solve = solver.solve()
    if solve != 0 and solve >= difficulty - 2:
        return solver
    return None


def generateNextBoard(prev, prevMoves, timeOut):
    width = len(prev)
    height = len(prev[0])
    for i in range(width - 1):
        for j in range(height):
            if prev[i][j] == 0:
                if getMillis() > timeOut:
                    return None
                prev[i][j] = 1
                if SOLVER.setBoard(prev).solve() > prevMoves:
                    return Solver(SOLVER, True)
                prev[i][j] = 0


def createBest(width, height, diff, duration):
    runs = 0
    val = 40_000 / width / height
    now = getMillis()
    solver = None
    while solver is None and (getMillis() - now) < duration * 1_000:
        solver = generateGameBoard(width, height, diff)
        runs += 1
        if runs % (val % diff) == 0:
            diff -= 1
    if solver is None:
        return None
    if (getMillis() - now) >= duration * 1_000:
        return solver
    while (getMillis() - now) < duration * 1_000:
        if solver.getSolvedMoves() is None:
            break
        newSolver = generateNextBoard(solver.getBoard(), len(solver.getSolvedMoves()), now + duration * 1000)
        if newSolver is None:
            break
        solver = newSolver
    if solver.getSolvedMoves() is None:
        return None
    return solver


def getArray(board):
    return "\n".join([" ".join(list(map(str, i))) for i in board])
