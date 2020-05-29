import docplex.mp as mp
import docplex.mp.model


class Theory(object):
    def __init__(self, *args):
        self.sentences = args

        self.m = mp.model.Model()
        self.gap = self.m.continuous_var()
        for s in self.sentences:
            s.configure(self.m, self.gap)

    def entails(self, query):
        query.compliment(self.m, self.gap)

        self.m.maximize(self.gap)
        return not (self.m.solve() and self.gap.solution_value > 0)


class Sentence(object):
    pass


class SimpleSentence(Sentence):
    def __init__(self, formula, ranges):
        self.formula = formula
        self.ranges = ranges
        self.active_range = None

    def configure(self, m, gap):
        self.formula.configure(m)

        self.active_range = m.binary_var_list(len(self.ranges))
        m.add_constraint(m.sum(self.active_range) == 1)
        for i in range(len(self.ranges)):
            self.ranges[i].configure(m, gap, self.formula, self.active_range[i])

    def compliment(self, m, gap):
        self.formula.configure(m)

        self.active_range = m.binary_var_list(len(self.ranges))
        for i in range(len(self.ranges)):
            self.ranges[i].compliment(m, gap, self.formula, self.active_range[i])


class RealRange(object):
    def __init__(self, lower, upper):
        self.lower = lower
        self.upper = upper


class ClosedRange(RealRange):
    def __init__(self, lower, upper):
        super().__init__(lower, upper)

    def configure(self, m, gap, formula, active):
        m.add_indicator(active, formula.val >= self.lower)
        m.add_indicator(active, formula.val <= self.upper)

    def compliment(self, m, gap, formula, active):
        m.add_indicator(active, formula.val <= self.lower - gap)
        m.add_indicator(active, formula.val >= self.upper + gap, 0)


class OpenRange(RealRange):
    def __init__(self, lower, upper):
        super().__init__(lower, upper)

    def configure(self, m, gap, formula, active):
        m.add_indicator(active, formula.val >= self.lower + gap)
        m.add_indicator(active, formula.val <= self.upper - gap)

    def compliment(self, m, gap, formula, active):
        m.add_indicator(active, formula.val <= self.lower)
        m.add_indicator(active, formula.val >= self.upper, 0)


class OpenLowerRange(RealRange):
    def __init__(self, lower, upper):
        super().__init__(lower, upper)

    def configure(self, m, gap, formula, active):
        m.add_indicator(active, formula.val >= self.lower + gap)
        m.add_indicator(active, formula.val <= self.upper)

    def compliment(self, m, gap, formula, active):
        m.add_indicator(active, formula.val <= self.lower)
        m.add_indicator(active, formula.val >= self.upper + gap, 0)


class OpenUpperRange(RealRange):
    def __init__(self, lower, upper):
        super().__init__(lower, upper)

    def configure(self, m, gap, formula, active):
        m.add_indicator(active, formula.val >= self.lower)
        m.add_indicator(active, formula.val <= self.upper - gap)

    def compliment(self, m, gap, formula, active):
        m.add_indicator(active, formula.val <= self.lower - gap)
        m.add_indicator(active, formula.val >= self.upper, 0)
