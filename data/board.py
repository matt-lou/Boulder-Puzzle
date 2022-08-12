from copy import deepcopy

import utils
from data.block import Block
from solver import Solver


class Board:
    def __init__(self, solver: Solver):
        if solver is None:
            return
        self._grid = deepcopy(solver.getBoard())
        self._moveList = solver.getSolvedMoves()
        if self._moveList is None:
            return
        self._moves = len(self._moveList)
        Block.resetId()
        self._board: [[Block]] = [[Block() if self._grid[x][y] == 1 else None for y in range(len(self._grid[0]))] for x
                                  in
                                  range(len(self._grid))]
        self._currentMoves = 0
        self._startTime = 0

    def regenerateMap(self):
        self._board = [[Block() if self._grid[x][y] == 1 else None for y in range(len(self._grid[0]))] for x in
                       range(len(self._grid))]
        self._currentMoves = 0

    def setStartTime(self):
        self._startTime = utils.getMillis()

    def getBoard(self):
        return self._board

    def getMoves(self):
        return self._moves

    def getCurrentMoves(self):
        return self._currentMoves

    def incrMoves(self):
        self._currentMoves += 1

    def getStartTime(self):
        return self._startTime

    def getMoveList(self):
        return self._moveList
