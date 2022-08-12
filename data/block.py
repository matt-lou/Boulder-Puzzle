from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor


class Block:
    BROWN = QBrush(QColor(191, 139, 6), Qt.SolidPattern)
    YELLOW = QBrush(QColor(240, 195, 79), Qt.SolidPattern)
    WHITE = QBrush(Qt.white, Qt.SolidPattern)
    RED = QBrush(Qt.red, Qt.SolidPattern)
    id = 0

    def __init__(self):
        self._blockColor = Block.BROWN if Block.id % 2 == 1 else Block.YELLOW
        Block.id += 1

    def getColor(self):
        return self._blockColor

    @staticmethod
    def resetId():
        Block.id = 0
