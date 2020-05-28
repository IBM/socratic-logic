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
        self.active_range = None

    def configure(self, m):
        self.formula.configure(m)

        self.active_range = m.binary_var_list(len(self.ranges))
        m.add_indicators(self.active_range, (self.formula.val >= r.lower for r in self.ranges))
        m.add_indicators(self.active_range, (self.formula.val <= r.upper for r in self.ranges))
        m.add_constraint(m.sum(self.active_range) == 1)

class RealRange(object):
    pass


class ClosedRange(RealRange):
    def __init__(self, lower, upper):
        self.lower = lower
        self.upper = upper
