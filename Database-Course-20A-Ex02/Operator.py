from abc import ABC, abstractmethod


class Operator(ABC):
    def __init__(self, operatorName, description, tables):
        self.operatorName = operatorName
        self.description = description
        self.tables = tables

    def setOperatorName(self, operatorName):
        self.operatorName = operatorName

    def getOperatorName(self):
        return self.operatorName

    def setDescription(self, description):
        self.description = description

    def getDescription(self):
        return self.description

    def setTables(self, tables):
        self.tables = tables

    def getTables(self):
        return self.tables