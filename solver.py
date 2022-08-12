# from __future__ import annotations
import collections
from copy import deepcopy

import sortedcontainers

import utils
from data.move import Move
from data.point import Point
from data.route import Route


class Solver:

    def __init__(self, other, clone: bool = False):
        if clone:
            self.grid = other.grid
            self.board = other.board
            self.routes = other.routes
            self.visited = other.visited
            self.solvedMoves = other.solvedMoves
            self.solvedPaths = other.solvedPaths
        else:
            self.grid = other
            self.board = other
            self.solvedPaths = 0
            self.routes = collections.deque()
            self.visited = set()
            self.solvedMoves = None

    def setBoard(self, board: [[]]):
        self.grid = board
        self.board = board
        self.solvedPaths = 0
        self.routes.clear()
        self.visited.clear()
        self.solvedMoves = None
        return self

    def solve(self) -> int:
        first = Route()
        first.grid = self.grid
        first.player = Point(len(self.grid) - 1, 0)
        self.routes = collections.deque()
        self.visited = set()
        self.routes.append(first)
        solvedRoutes = sortedcontainers.SortedSet()
        startTime = utils.getMillis()
        while len(self.routes) > 0:
            if utils.getMillis() - startTime > 5000:
                if self.solvedPaths == 0:
                    return 0
                else:
                    break
            if self.solvedPaths > 5:
                break

            r = self.routes.popleft()
            if r is None:
                continue
            gridCode = Solver._getGridCode(r.grid)
            if gridCode in self.visited:
                continue
            self.visited.add(gridCode)

            start = r.player
            if start.getX() == 0:
                solvedRoutes.add(r)
                self.solvedPaths += 1
                continue
            self.grid = r.grid

            playerLocs = set()
            pMoves = collections.deque()
            pMoves.append(start)

            while len(pMoves) > 0:
                loc = pMoves.popleft()
                if loc in playerLocs:
                    continue
                playerLocs.add(loc)

                moves = self._validMoves(loc)
                for p1 in moves:
                    if p1.getX() == -1:
                        solvedRoutes.add(r)
                        self.solvedPaths += 1
                        pMoves.clear()
                        break
                    if self.grid[p1.getX()][p1.getY()] != 1:
                        pMoves.append(p1)

            for p in playerLocs:
                self._getValidPush(p, self.grid, self._validMoves(p), r)

        if self.solvedPaths != 0 and len(solvedRoutes) > 0:
            first1 = solvedRoutes.pop(0)
            if first1 is None:
                return 0
            self.solvedMoves = first1.moveList
            return len(first1.moveList)
        else:
            return 0

    def getBoard(self) -> [[]]:
        return self.board

    def getSolvedMoves(self):
        return self.solvedMoves

    def _getValidPush(self, start: Point, grid: [[]], moves, route: Route):
        p: Point
        for p in moves:
            if p.getX() == -1:
                continue
            newGrid = deepcopy(grid)
            push = Solver._push(start.getX(), start.getY(), p.getX(), p.getY(), newGrid)
            if push is not None:
                gridCode = Solver._getGridCode(newGrid)
                if gridCode not in self.visited:
                    r1 = deepcopy(route)
                    r1.moveList.append(push)
                    r1.moves += 1
                    r1.grid = newGrid
                    r1.player = push.p
                    try:
                        self.routes.append(r1)
                    except Exception as e:
                        print(f"Something went wrong: {e}")

    def _validMoves(self, start: Point) -> set:
        out = set()
        x = start.getX()
        y = start.getY()
        maxX = len(self.grid)
        maxY = len(self.grid[0])
        if 0 < y < maxY - 1:
            out.add(Point(x, y + 1))
            out.add(Point(x, y - 1))
        elif y == 0:
            out.add(Point(x, y + 1))
        elif y == maxY - 1:
            out.add(Point(x, y - 1))

        if -1 < x < maxX - 1:
            out.add(Point(x + 1, y))
            out.add(Point(x - 1, y))
        elif x == -1:
            out.add(Point(0, y))
        elif x == maxX - 1:
            out.add(Point(x - 1, y))
        return out

    @staticmethod
    def _getGridCode(grid: [[]]) -> int:
        val = 0
        for i in grid:
            val = 7 * val + utils.arrayHash(i)
        return val

    @staticmethod
    def _push(playerX: int, playerY: int, boxX: int, boxY: int, grid: [[]]):
        if grid[boxX][boxY] != 1:
            return None
        if boxX == 0 or boxX == len(grid) - 1:
            return None
        if boxX - playerX == -1:
            if grid[boxX - 1][boxY] == 0:
                grid[boxX - 1][boxY] = 1
                grid[boxX][boxY] = 0

                move = Move()
                move.p = Point(boxX, boxY)
                move.offsetType = 1
                return move
        elif boxX - playerX == 1:
            if grid[boxX + 1][boxY] == 0:
                grid[boxX + 1][boxY] = 1
                grid[boxX][boxY] = 0

                move = Move()
                move.p = Point(boxX, boxY)
                move.offsetType = 2
                return move
        elif boxY - playerY == -1:
            if boxY == 0:
                return None
            if grid[boxX][boxY - 1] == 0:
                grid[boxX][boxY - 1] = 1
                grid[boxX][boxY] = 0

                move = Move()
                move.p = Point(boxX, boxY)
                move.offsetType = 3
                return move
        elif boxY - playerY == 1:
            if boxY == len(grid[0]) - 1:
                return None
            if grid[boxX][boxY + 1] == 0:
                grid[boxX][boxY + 1] = 1
                grid[boxX][boxY] = 0

                move = Move()
                move.p = Point(boxX, boxY)
                move.offsetType = 4
                return move
        return None

    @staticmethod
    def _swap(grid, x1: int, y1: int, x2: int, y2: int) -> bool:
        temp = grid[x1][y1]
        if temp is not None:
            return False
        grid[x1][y1] = grid[x2][y2]
        grid[x2][y2] = None
        return True

    @staticmethod
    def attemptMove(player: Point, offsetType: int, board) -> bool:
        if player is None:
            return False
        if player.getX() < 0:
            return False
        if player.getY() == 0 and offsetType == 3:
            return False
        if player.getY() == len(board[0]) - 1 and offsetType == 4:
            return False
        if player.getX() == len(board) - 1 and offsetType == 2:
            return False

        move = Point(player.getX(), player.getY())
        m = Move()
        m.p = move
        m.offsetType = offsetType

        if offsetType == 1:
            move.translate(-1, 0)
            if board[move.getX()][move.getY()] is None:
                player.translate(-1, 0)
            elif Solver.pushMove(m, board):
                player.translate(-1, 0)
                return True
        elif offsetType == 2:
            move.translate(1, 0)
            if board[move.getX()][move.getY()] is None:
                player.translate(1, 0)
            elif Solver.pushMove(m, board):
                player.translate(1, 0)
                return True
        elif offsetType == 3:
            move.translate(0, -1)
            if board[move.getX()][move.getY()] is None:
                player.translate(0, -1)
            elif Solver.pushMove(m, board):
                player.translate(0, -1)
                return True
        elif offsetType == 4:
            move.translate(0, 1)
            if board[move.getX()][move.getY()] is None:
                player.translate(0, 1)
            elif Solver.pushMove(m, board):
                player.translate(0, 1)
                return True
        return False

    @staticmethod
    def pushMove(move: Move, grid) -> bool:
        boxX = move.p.getX()
        boxY = move.p.getY()
        if move.offsetType == 1:
            if boxX == 0:
                return False
            return Solver._swap(grid, boxX - 1, boxY, boxX, boxY)
        elif move.offsetType == 2:
            if boxX == len(grid) - 1:
                return False
            return Solver._swap(grid, boxX + 1, boxY, boxX, boxY)
        elif move.offsetType == 3:
            if boxY == 0:
                return False
            return Solver._swap(grid, boxX, boxY - 1, boxX, boxY)
        elif move.offsetType == 4:
            if boxY == len(grid[0]) - 1:
                return False
            return Solver._swap(grid, boxX, boxY + 1, boxX, boxY)
