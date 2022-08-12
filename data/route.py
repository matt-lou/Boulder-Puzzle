import collections
from functools import total_ordering

import utils
from data.point import Point


@total_ordering
class Route:
    def __init__(self):
        self.grid: [[]] = None
        self.player = None
        self.moveList = collections.deque()
        self.moves: int = 0

    def __eq__(self, other):
        if other is self:
            return True
        if not isinstance(other, Route):
            return False
        return self.grid == other.grid

    def __hash__(self):
        if self.grid is None:
            return 0
        total = 0
        for i in self.grid:
            total = 31 * total + utils.arrayHash(i)
        return total

    def __lt__(self, other):
        return self.moves < other.moves

    def __str__(self):
        return "Route{Player=" + str((self.player if self.player else Point())) + ", Moves=" + str(self.moves) + "}"
