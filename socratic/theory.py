import docplex.mp as mp
import docplex.mp.model


class Theory(object):
    def __init__(self, *args):
        self.sentences = args

        self.m = mp.model.Model()
        for s in self.sentences:
            s.configure(self.m)

    def entails(self, query):
        pass


class Sentence(object):
    pass


class SimpleSentence(Sentence):
    def __init__(self, formula, ranges):
        self.formula = formula
        self.ranges = ranges

    def configure(self, m):
        self.formula.configure(m)

        m.add_constraint(self.formula.val >= self.ranges[0].lower)
        m.add_constraint(self.formula.val <= self.ranges[0].upper)


class RealRange(object):
    pass


class ClosedRange(RealRange):
    def __init__(self, lower, upper):
        self.lower = lower
        self.upper = upper
