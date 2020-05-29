import docplex.mp as mp
import docplex.mp.model


class Theory(object):
    def __init__(self, *args):
        self.sentences = args

    def entails(self, query):
        m = mp.model.Model()
        gap = m.continuous_var(lb=0, ub=1)

        for s in self.sentences:
            s.configure(m, gap)
        query.compliment(m, gap)

        m.maximize(gap)
        res = not (m.solve() and gap.solution_value > 0)
        m.end()

        for s in self.sentences:
            s.reset()
        query.reset()

        return res


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

    def reset(self):
        self.formula.reset()

        self.active_range = None


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
