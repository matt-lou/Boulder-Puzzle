class Point:
    def __init__(self, x=0, y=0):
        self._x = x
        self._y = y

    def getX(self) -> int:
        return self._x

    def getY(self) -> int:
        return self._y

    def translate(self, dx: int, dy: int) -> None:
        self._x += dx
        self._y += dy

    def __str__(self):
        return f"({self._x},{self._y})"

    def __eq__(self, other):
        if other is self:
            return True
        if not isinstance(other, Point):
            return False
        return self._x == other._x and self._y == other._y

    def __hash__(self):
        return 15 * self._x + self._y
