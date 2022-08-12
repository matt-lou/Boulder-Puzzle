import collections
import sys

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QRect, pyqtSlot, QThreadPool, QRunnable, QTimer, \
    QCoreApplication
from PyQt5.QtGui import QPainter, QBrush, QColor, QPalette
from PyQt5.QtWidgets import QMainWindow, QPushButton

import utils
from data.block import Block
from data.board import Board
from data.point import Point
from solver import Solver


class Canvas(QMainWindow):
    def __init__(self, game):
        super().__init__()
        self.height = 550
        self.width = 900
        self.resize(self.width, self.height)
        self.game = game
        self.scaled = 1
        self.leftMargin = 0
        self.rightMargin = self.width - 120
        self.buttonsHidden = True
        self._initUI()

    def _initUI(self):
        self.setWindowTitle("Boulder Puzzle")

        @pyqtSlot()
        def createNewBoard():
            if self._newButton.isFlat():
                return
            self.game.createNewGame()
            self.game.decreaseScore()
            self.repaint()

        @pyqtSlot()
        def showMoves():
            if self._showMoves.isFlat():
                return
            self.game.decreaseScore(1)
            self.game.toggleShowMoves()
            self.hideButton(2)
            self.repaint()

        @pyqtSlot()
        def showSolution():
            if self._showSolution.isFlat():
                return
            self.game.showSolution()
            self.game.decreaseScore(4)
            self.hideButton(3)
            self.repaint()

        self._newButton = QPushButton("New Board", self)
        self._newButton.setToolTip("Creates a new board (if unsolvable or too difficult) (-2 points)")
        self._newButton.clicked.connect(createNewBoard)
        self._newButton.visible = False

        self._resetButton = QPushButton("Reset Map (R)", self)
        self._resetButton.clicked.connect(self.game.resetMap)
        self._resetButton.visible = False

        self._showMoves = QPushButton("Show Moves Needed", self)
        self._showMoves.setToolTip("Shows the number of moves needed to solve the puzzle (-1 point)")
        self._showMoves.clicked.connect(showMoves)
        self._showMoves.resize(self._showMoves.size().width() * 1.5, self._showMoves.size().height())
        self._showMoves.visible = False

        self._showSolution = QPushButton("Show Solution", self)
        self._showSolution.setToolTip("Displays solution for puzzle (-4 points)")
        self._showSolution.clicked.connect(showSolution)
        self._showSolution.visible = False

        self._showHelp = QPushButton("Help", self)
        self._showHelp.setToolTip("Displays the tutorial again.")
        self._showHelp.clicked.connect(self.game.showHelp)
        self._showHelp.visible = False

        self.moveButtons()

    def moveButtons(self):
        alpha = (self.width - self.rightMargin) // 2 + self.rightMargin - 50
        beta = self.leftMargin // 2 - 50

        self._newButton.move(alpha, self.height // 2)
        self._resetButton.move(beta, self.height // 2)
        self._showMoves.move(beta - 25, self.height // 3)
        self._showSolution.move(beta, 2 * self.height // 3)
        self._showHelp.move(alpha, 2 * self.height // 3)

    def showButton(self, index):
        if index == 0:
            button = self._newButton
        elif index == 1:
            button = self._resetButton
        elif index == 2:
            button = self._showMoves
        elif index == 3:
            button = self._showSolution
        else:
            button = self._showHelp
        button.setPalette(QPalette())
        button.setFlat(False)

    def hideButton(self, index):
        palette = QPalette(Qt.transparent, Qt.transparent, Qt.transparent, Qt.transparent,
                           Qt.transparent, Qt.transparent, Qt.transparent, Qt.transparent,
                           Qt.transparent)
        if index == 0:
            button = self._newButton
        elif index == 1:
            button = self._resetButton
        elif index == 2:
            button = self._showMoves
        elif index == 3:
            button = self._showSolution
        else:
            button = self._showHelp
        button.setPalette(palette)
        button.setFlat(True)

    def showButtons(self, show: bool):
        palette = QPalette() if show else QPalette(Qt.transparent, Qt.transparent, Qt.transparent, Qt.transparent,
                                                   Qt.transparent, Qt.transparent, Qt.transparent, Qt.transparent,
                                                   Qt.transparent)
        self._newButton.setPalette(palette)
        self._resetButton.setPalette(palette)
        self._showMoves.setPalette(palette)
        self._showSolution.setPalette(palette)
        self._showHelp.setPalette(palette)

        self._newButton.setFlat(not show)
        self._resetButton.setFlat(not show)
        self._showMoves.setFlat(not show)
        self._showSolution.setFlat(not show)
        self._showHelp.setFlat(not show)

    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        self.game.handleMoves(e)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QPainter()
        painter.begin(self)
        self.game.paint(painter)
        painter.end()


class Game:

    def __init__(self, rows, cols):
        self._score = 10
        self._rows = rows
        self._cols = cols
        self._solved = 0
        self._movesTaken = ""
        self._timeTaken = ""
        self._moves = ""

        self._congratulationTicks = 0
        self._showHelp = 1

        self._board = None
        self._game = None
        self._showMoves = False
        self._showSolution = False
        self._gameOver = False
        self._calculating = False
        self._generatingMulti = False
        self._player = None
        self._games = collections.deque()

        self._app = QtWidgets.QApplication(sys.argv)
        self._canvas = Canvas(self)

    def start(self):
        self._canvas.show()
        self._canvas.repaint()

        def tick():
            self._canvas.repaint()
            self._generateBoards()
            self._handleLogic()

        timer = QTimer()
        timer.timeout.connect(tick)
        timer.setInterval(50)
        timer.start()

        QCoreApplication.quit()
        sys.exit(self._app.exec_())

    def handleMoves(self, e: QtGui.QKeyEvent):
        if self._gameOver:
            self.restart()
            # self._canvas.repaint()
            return
        elif self._showHelp != 0:
            self._showHelp += 1
            # self._canvas.repaint()
            return
        elif self._congratulationTicks != 0:
            self._congratulationTicks = 0
            # self._canvas.repaint()
            return
        if self._player is None:
            return
        offsetType: int = 0
        key = e.key()
        if key == Qt.Key_W:
            offsetType = 1
            if self._player.getX() == 0:
                self._player = None
                self._congratulationTicks = 100
                if self._board.getCurrentMoves() == self._board.getMoves():
                    self._score += 1
                self._movesTaken = f"Moves Needed: {self._board.getMoves()}. Moves Taken: {self._board.getCurrentMoves()}"
                time = utils.getMillis() - self._board.getStartTime()
                if time < 20_000:
                    self._score += 1
                self._timeTaken = f"Time Taken: {time / 1000} seconds."
                self.createNewGame()
                self._score += 2
                self._solved += 1
        elif key == Qt.Key_A:
            offsetType = 3
        elif key == Qt.Key_S:
            offsetType = 2
        elif key == Qt.Key_D:
            offsetType = 4
        if key == Qt.Key_R:
            self.resetMap()
            return

        if offsetType != 0:
            if self._board is None:
                return
            if Solver.attemptMove(self._player, offsetType, self._game):
                self._board.incrMoves()
                if self._board.getCurrentMoves() == 1:
                    self._canvas.hideButton(3)
            # self._canvas.repaint()

    def _handleLogic(self):
        if self._score <= 0:
            self._gameOver = True
            # self._canvas.repaint()

    def _generateBoards(self):
        if self._board is None:
            if len(self._games) == 0:
                if not self._generatingMulti and not self._calculating:
                    self._calculating = True

                    def backgroundCreate():
                        best = utils.createBest(self._rows, self._cols, 3, 10)
                        if best is not None:
                            self._board = Board(best)
                            self._game = self._board.getBoard()
                            self._board.setStartTime()
                            self._showMoves = False
                            self._showSolution = False
                            self._player = Point(len(self._game) - 1, 0)
                        self._calculating = False
                        # # self._canvas.repaint()

                    # # # self._canvas.repaint() <- something..

                    # threading.Thread(target=backgroundCreate).start()
                    class Runnable(QRunnable):
                        def __init__(self):
                            super().__init__()

                        def run(self):
                            backgroundCreate()

                    threadCount = QThreadPool.globalInstance().maxThreadCount()
                    pool = QThreadPool.globalInstance()
                    if threadCount > 0:
                        runnable = Runnable()
                        pool.start(runnable)
                    # Multithreading?
            else:
                self._board: Board = self._games.pop()
                self._calculating = False
                self._game = self._board.getBoard()
                self._board.setStartTime()
                self._showSolution = self._showMoves = False
                self._player = Point(len(self._game) - 1, 0)
                # self._canvas.repaint()
        else:
            if len(self._games) < 2:
                if not self._generatingMulti:
                    self._generatingMulti = True

                    def multiCreate():
                        while self._generatingMulti:
                            best = utils.createBest(self._rows, self._cols, 3, 30)
                            if best is not None:
                                self._games.append(Board(best))

                    class Runnable(QRunnable):
                        def __init__(self):
                            super().__init__()

                        def run(self):
                            multiCreate()

                    threadCount = QThreadPool.globalInstance().maxThreadCount()
                    pool = QThreadPool.globalInstance()
                    if threadCount > 0:
                        runnable = Runnable()
                        pool.start(runnable)
            else:
                self._generatingMulti = False
            self._calculating = False

    def resetMap(self):
        Block.resetId()
        if self._board is not None:
            self._board.regenerateMap()
            self._game = self._board.getBoard()
            self._showSolution = False
            self._score -= 1
            self._canvas.showButton(3)
        self._player = Point(len(self._game) - 1, 0)
        # self._canvas.repaint()

    def restart(self):
        self._score = 10
        self._solved = 0
        self._congratulationTicks = 0
        self._moves = ""
        self._board = None
        self._game = None
        self._showMoves = False
        self._showSolution = False
        self._gameOver = False

    def createNewGame(self):
        self._game = None
        self._board = None

    def paint(self, painter):
        size = self._canvas.size()
        if self._canvas.buttonsHidden:
            self._canvas.showButtons(False)
        if int(size.width()) != int(self._canvas.width) or int(size.height()) != int(self._canvas.height):
            self._canvas.width = int(size.width())
            self._canvas.height = int(size.height())
            self._canvas.rightMargin = self._canvas.width - 120
            self._canvas.moveButtons()

        if self._gameOver:
            self._canvas.buttonsHidden = True
            self._showGameOver(painter)
            return
        if 7 > self._showHelp > 0:
            self._canvas.buttonsHidden = True
            self._drawHelp(painter)
            return
        elif self._showHelp > 6:
            self._showHelp = 0
        if self._congratulationTicks != 0:
            self._canvas.buttonsHidden = True
            self._drawCongratulation(painter)
            return

        self._drawBoard(painter)

    def drawCenteredString(self: QPainter, text, y, height=50, left=0, right=0):
        if right == 0:
            right = self.device().width
        rect = QRect(left, y - 25, right, height)
        self.drawText(rect, Qt.AlignCenter, text)

    QPainter.drawCenteredString = drawCenteredString

    def _drawBoard(self, painter):
        # print("hello")
        if self._game is None:
            # print("Generating Board...")
            font = painter.font()
            font.setPixelSize(42)
            painter.setFont(font)
            painter.setPen(QColor(50, 158, 168))
            painter.drawCenteredString("Generating Board...", self._canvas.height / 2)
            self._canvas.buttonsHidden = True
            return
        if self._canvas.buttonsHidden:
            self._canvas.showButtons(True)
            self._canvas.buttonsHidden = False
        c1 = self._canvas.width - 40
        c2 = self._canvas.height - 60

        hlength = len(self._board.getBoard()[0])
        c1 /= hlength
        c1 = int(c1)
        vlength = len(self._board.getBoard())
        c2 /= vlength
        c2 = int(c2)
        squareSize = min(c1, c2)
        self._canvas.leftMargin = int((self._canvas.width - squareSize * hlength) / 2)
        topMargin = int((self._canvas.height - squareSize * vlength) / 2 + 20)

        painter.setBrush(QBrush(Qt.green, Qt.SolidPattern))
        painter.drawRect(self._canvas.leftMargin, 10, hlength * squareSize, vlength * squareSize)
        rightMargin = self._canvas.leftMargin + hlength * squareSize
        if rightMargin != self._canvas.rightMargin:
            self._canvas.rightMargin = rightMargin
            self._canvas.moveButtons()
        for i in range(hlength):
            for j in range(vlength):
                block: Block = self._game[j][i]
                if block is not None:
                    painter.setBrush(block.getColor())
                else:
                    painter.setBrush(Block.WHITE)
                painter.drawRect(self._canvas.leftMargin + i * squareSize, topMargin + j * squareSize, squareSize,
                                 squareSize)

        if self._player is not None:
            painter.setBrush(Block.RED)
            painter.drawRect(self._canvas.leftMargin + self._player.getY() * squareSize + squareSize / 4,
                             topMargin + self._player.getX() * squareSize + squareSize / 4, squareSize / 2,
                             squareSize / 2)

        if self._showSolution:
            counter = 0
            for move in self._board.getMoveList():
                if self._board.getCurrentMoves() > counter:
                    counter += 1
                    continue
                counter += 1

                x = int(move.p.getY() * squareSize + self._canvas.leftMargin + squareSize / 2)
                y = int(move.p.getX() * squareSize + topMargin + squareSize / 2)
                x2 = x
                y2 = y
                offsetType = move.offsetType
                if offsetType == 1:
                    y2 += squareSize
                elif offsetType == 2:
                    y2 -= squareSize
                elif offsetType == 3:
                    x2 += squareSize
                elif offsetType == 4:
                    x2 -= squareSize
                if counter - 1 == self._board.getCurrentMoves():
                    painter.setPen(Qt.green)
                    painter.setBrush(QBrush(Qt.green, Qt.SolidPattern))
                else:
                    painter.setPen(Qt.red)
                    painter.setBrush(Block.RED)
                painter.drawLine(x, y, x2, y2)

                painter.translate(x, y)
                theta = 0
                if offsetType == 3:
                    theta = 180
                elif offsetType == 1:
                    theta = 270
                elif offsetType == 2:
                    theta = 90
                painter.rotate(theta)
                painter.drawLine(-squareSize / 3, -squareSize / 3, 0, 0)
                painter.drawLine(-squareSize / 3, squareSize / 3, 0, 0)
                painter.rotate(-theta)
                painter.translate(-x, -y)

        font = painter.font()
        font.setPixelSize(12)
        painter.setFont(font)
        if self._showMoves:
            painter.setPen(Qt.red)
            painter.drawCenteredString(f"Needed Moves: {self._board.getMoves()}", 20, left=5,
                                       right=self._canvas.leftMargin - 5)
        painter.setPen(Qt.black)
        painter.drawCenteredString(f"Points: {self._score}", y=self._canvas.height // 3,
                                   left=self._canvas.rightMargin + 5,
                                   right=self._canvas.width - 10 - self._canvas.rightMargin)

    def _drawCongratulation(self, painter):  # drawText method
        self._congratulationTicks -= 1
        font = painter.font()
        font.setPixelSize(32)
        painter.setFont(font)
        painter.setPen(QColor(50, 158, 168))
        painter.drawCenteredString("Congratulations! Click any letter key to move on.", self._canvas.height / 2)
        painter.drawCenteredString(self._movesTaken, 2 * self._canvas.height / 3)
        painter.drawCenteredString(self._timeTaken, 2 * self._canvas.height / 3 + 40)
        pass

    def _drawHelp(self, painter):
        font = painter.font()
        font.setPixelSize(32)
        painter.setFont(font)
        painter.setPen(QColor(50, 158, 168))
        if self._showHelp == 1:
            painter.drawCenteredString("Welcome! This game is called Boulder", self._canvas.height / 3)
            painter.drawCenteredString("..and it is a procedurally generated puzzle game", self._canvas.height / 2)
            # g.setColor(new Color(50, 158, 168).darker());
            painter.drawCenteredString("Click any letter key to continue", int(4 * self._canvas.height / 5))
        elif self._showHelp == 2:
            painter.drawCenteredString("..Which means that it should (theoretically)", self._canvas.height / 3)
            painter.drawCenteredString("..allow you to play it infinitely!", 2 * self._canvas.height / 3)
            #     # g.setColor(new Color(50, 158, 168).darker());
            painter.drawCenteredString("Click any letter key to continue", 4 * self._canvas.height / 5)
        elif self._showHelp == 3:
            painter.drawCenteredString("The goal is simple.", self._canvas.height / 3)
            painter.drawCenteredString("Get to the end by pushing boulders", 2 * self._canvas.height / 3)
            #     # g.setColor(new Color(50, 158, 168).darker());
            painter.drawCenteredString("Click any letter key to continue", 4 * self._canvas.height / 5)
        elif self._showHelp == 4:
            painter.drawCenteredString("You may use WASD to move", self._canvas.height / 3)
            painter.drawCenteredString("..but you can only push 1 boulder at a time", 2 * self._canvas.height / 3)
            #     # g.setColor(new Color(50, 158, 168).darker());
            painter.drawCenteredString("Click any letter key to continue", 4 * self._canvas.height / 5)
        elif self._showHelp == 5:
            painter.drawCenteredString("Every level you complete will give you 2 points", 2 * self._canvas.height / 6)
            painter.drawCenteredString("Resetting/showing total moves will subtract a point",
                                       3 * self._canvas.height / 6)
            painter.drawCenteredString("And showing a solution will subtract 4", 4 * self._canvas.height / 6)
            #     # g.setColor(new Color(50, 158, 168).darker());
            painter.drawCenteredString("Click any letter key to continue", 5 * self._canvas.height / 6)
        elif self._showHelp == 6:
            painter.drawCenteredString("A bonus point will be awarded for pushing the fewest ",
                                       2 * self._canvas.height / 6)
            painter.drawCenteredString("boulders, and another point for solving it quickly.",
                                       3 * self._canvas.height / 6)
            # elif self._showHelp == 7:
            painter.drawCenteredString("Good Luck!", 5 * self._canvas.height / 7)
        elif self._showHelp != 0:
            self._showHelp = 0
        # painter.drawCenteredString("Hello There", self._canvas.height / 3)
        pass

    def _showGameOver(self, painter):
        font = painter.font()
        font.setPixelSize(20)
        painter.setFont(font)
        painter.setPen(QColor(50, 158, 168))
        painter.drawCenteredString(f"You completed: {self._solved} boards!", 2 * self._canvas.height / 3)
        painter.drawCenteredString("Click any letter key to restart", 2 * self._canvas.height / 3 + 20)
        painter.setPen(Qt.red)
        font = painter.font()
        font.setPixelSize(50)
        painter.setFont(font)
        painter.drawCenteredString("Game Over!", self._canvas.height / 2)
        pass

    def decreaseScore(self, score=2):
        self._score -= score

    def toggleShowMoves(self):
        self._showMoves = not self._showMoves
        # self._canvas.repaint()

    def showSolution(self):
        self._showSolution = True

    def showHelp(self):
        self._showHelp = 1
