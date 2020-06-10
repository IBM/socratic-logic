from collections.abc import Iterable
from numbers import Number

import docplex.mp as mp
import docplex.mp.model

from socratic.op import Logic


class Theory(object):
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], Iterable):
            args = args[0]

        self.sentences = args

    def satisfiable(self, logic=Logic.LUKASIEWICZ):
        return not self.entails(None, logic)

    def entails(self, query, logic=Logic.LUKASIEWICZ):
        m = mp.model.Model()
        gap = m.continuous_var(lb=0, ub=1, name="gap")

        for s in self.sentences:
            s.configure(m, gap, logic)
        if query is not None:
            query.compliment(m, gap, logic)

        m.maximize(gap)
        res = not (m.solve() and gap.solution_value > 0)
        m.end()

        for s in self.sentences:
            s.reset()
        if query is not None:
            query.reset()

        return res


class Sentence(object):
    pass


class SimpleSentence(Sentence):
    def __init__(self, formula, ranges):
        if not isinstance(ranges, Iterable):
            ranges = [ranges]

        self.formula = formula
        self.ranges = [Point(r) if isinstance(r, Number) else r for r in ranges]

    def configure(self, m, gap, logic):
        self.formula.configure(m, gap, logic)

        active_range = m.binary_var_list(len(self.ranges), name=str(self.formula) + ".active_range")
        m.add_constraint(m.sum(active_range) == 1)
        for i in range(len(self.ranges)):
            self.ranges[i].configure(m, gap, self.formula, active_range[i])

    def compliment(self, m, gap, logic):
        self.formula.configure(m, gap, logic)

        active_range = m.binary_var_list(len(self.ranges), name=str(self.formula) + ".active_range")
        for i in range(len(self.ranges)):
            self.ranges[i].compliment(m, gap, self.formula, active_range[i])

    def reset(self):
        self.formula.reset()


class RealRange(object):
    def __init__(self, lower, upper):
        self.lower = lower
        self.upper = upper

    def configure(self, m, gap, formula, active):
        pass

    def compliment(self, m, gap, formula, active):
        pass


class ClosedRange(RealRange):
    def configure(self, m, gap, formula, active):
        m.add_indicator(active, formula.val >= self.lower)
        m.add_indicator(active, formula.val <= self.upper)

    def compliment(self, m, gap, formula, active):
        m.add_indicator(active, formula.val <= self.lower - gap)
        m.add_indicator(active, formula.val >= self.upper + gap, 0)


class Point(ClosedRange):
    def __init__(self, point):
        super().__init__(point, point)


class OpenRange(RealRange):
    def configure(self, m, gap, formula, active):
        m.add_indicator(active, formula.val >= self.lower + gap)
        m.add_indicator(active, formula.val <= self.upper - gap)

    def compliment(self, m, gap, formula, active):
        m.add_indicator(active, formula.val <= self.lower)
        m.add_indicator(active, formula.val >= self.upper, 0)


class OpenLowerRange(RealRange):
    def configure(self, m, gap, formula, active):
        m.add_indicator(active, formula.val >= self.lower + gap)
        m.add_indicator(active, formula.val <= self.upper)

    def compliment(self, m, gap, formula, active):
        m.add_indicator(active, formula.val <= self.lower)
        m.add_indicator(active, formula.val >= self.upper + gap, 0)


class OpenUpperRange(RealRange):
    def configure(self, m, gap, formula, active):
        m.add_indicator(active, formula.val >= self.lower)
        m.add_indicator(active, formula.val <= self.upper - gap)

    def compliment(self, m, gap, formula, active):
        m.add_indicator(active, formula.val <= self.lower - gap)
        m.add_indicator(active, formula.val >= self.upper, 0)
