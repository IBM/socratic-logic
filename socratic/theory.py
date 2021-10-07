from abc import ABC, abstractmethod
from collections.abc import Iterable
from numbers import Number

import docplex.mp as mp
import docplex.mp.model

from socratic.op import Logic


class Theory(object):
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], Iterable):
            args = args[0]

        self.sentences = list(args)

        self.m = None
        self.gap = None

    def satisfiable(self, logic=Logic.LUKASIEWICZ):
        return not self.entails(None, logic)

    def entails(self, query, logic=Logic.LUKASIEWICZ):
        self.m = mp.model.Model(cts_by_name=True)
        self.m.float_precision = 16
        self.gap = self.m.continuous_var(lb=0, ub=1, name="gap")

        for s in self.sentences:
            s.reset()
        if query is not None:
            query.reset()

        for s in self.sentences:
            s.configure(self.m, self.gap, logic)
        if query is not None:
            query.compliment(self.m, self.gap, logic)

        self.m.maximize(self.gap)
        res = not (self.m.solve() and self.gap.solution_value > 1e-8)

        return res


class Sentence(ABC):
    pass


class SimpleSentence(Sentence):
    def __init__(self, formula, intervals):
        if not isinstance(intervals, Iterable):
            intervals = [intervals]

        self.formula = formula
        self.intervals = [Point(r) if isinstance(r, Number) else r for r in intervals]

    def reset(self):
        self.formula.reset()

    def configure(self, m, gap, logic):
        self.formula.configure(m, gap, logic)

        active_interval = m.binary_var_list(len(self.intervals), name=repr(self.formula) + ".active_interval")
        m.add_constraint(m.sum(active_interval) == 1)
        for i in range(len(self.intervals)):
            self.intervals[i].configure(m, gap, self.formula, active_interval[i])

    def compliment(self, m, gap, logic):
        self.formula.configure(m, gap, logic)

        active_interval = m.binary_var_list(len(self.intervals), name=repr(self.formula) + ".active_interval")
        for i in range(len(self.intervals)):
            self.intervals[i].compliment(m, gap, self.formula, active_interval[i])


class FloatInterval(ABC):
    def __init__(self, lower, upper):
        self.lower = lower
        self.upper = upper

    @abstractmethod
    def configure(self, m, gap, formula, active):
        pass

    @abstractmethod
    def compliment(self, m, gap, formula, active):
        pass


class ClosedInterval(FloatInterval):
    def configure(self, m, gap, formula, active):
        m.add_indicator(active, formula.val >= self.lower)
        m.add_indicator(active, formula.val <= self.upper)

    def compliment(self, m, gap, formula, active):
        m.add_indicator(active, formula.val <= self.lower - gap)
        m.add_indicator(active, formula.val >= self.upper + gap, 0)


class Point(ClosedInterval):
    def __init__(self, point):
        super().__init__(point, point)


class AtLeast(ClosedInterval):
    def __init__(self, lower):
        super().__init__(lower, 1)


class AtMost(ClosedInterval):
    def __init__(self, upper):
        super().__init__(0, upper)


class OpenInterval(FloatInterval):
    def configure(self, m, gap, formula, active):
        m.add_indicator(active, formula.val >= self.lower + gap)
        m.add_indicator(active, formula.val <= self.upper - gap)

    def compliment(self, m, gap, formula, active):
        m.add_indicator(active, formula.val <= self.lower)
        m.add_indicator(active, formula.val >= self.upper, 0)


class OpenLowerInterval(FloatInterval):
    def configure(self, m, gap, formula, active):
        m.add_indicator(active, formula.val >= self.lower + gap)
        m.add_indicator(active, formula.val <= self.upper)

    def compliment(self, m, gap, formula, active):
        m.add_indicator(active, formula.val <= self.lower)
        m.add_indicator(active, formula.val >= self.upper + gap, 0)


class GreaterThan(OpenLowerInterval):
    def __init__(self, lower):
        super().__init__(lower, 1)


class OpenUpperInterval(FloatInterval):
    def configure(self, m, gap, formula, active):
        m.add_indicator(active, formula.val >= self.lower)
        m.add_indicator(active, formula.val <= self.upper - gap)

    def compliment(self, m, gap, formula, active):
        m.add_indicator(active, formula.val <= self.lower - gap)
        m.add_indicator(active, formula.val >= self.upper, 0)


class LessThan(OpenUpperInterval):
    def __init__(self, upper):
        super().__init__(0, upper)
