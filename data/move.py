class Move:
    def __init__(self):
        self.p = None
        self.offsetType = None

    def __str__(self):
        return "Move{" + "p=" + str(self.p) + ", offsetType=" + str(self.offsetType) + '}'

    pass
