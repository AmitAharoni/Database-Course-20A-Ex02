from Operator import Operator

class NJoin(Operator):
    def __init__(self, description, tables):
        super(NJoin, self).__init__("NJoin", None, tables) # (",R"), ("R,") , ("S,R") , None

    def isOperatorInFirst(self):
        return self.tables is None or self.tables.index(',') == 0

    def isOperatorInSecond(self):
        return self.tables is None or self.tables.endswith(',')