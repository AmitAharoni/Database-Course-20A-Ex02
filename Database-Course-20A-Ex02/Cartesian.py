from Operator import Operator

class Cartesian(Operator):
    def __init__(self, description, tables):
        super(Cartesian, self).__init__("Cartesian", None, tables)  # (",R"), ("R,") , ("S,R") ###

    def isOperatorInFirst(self):
        return self.tables is None or self.tables.index(',') == 0

    def isOperatorInSecond(self):
        return self.tables is None or self.tables.endswith(',')