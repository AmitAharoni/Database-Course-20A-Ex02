from Operator import Operator

class Sigma(Operator):
    def __init__(self, description, tables):
       super(Sigma, self).__init__("Sigma", description, tables)