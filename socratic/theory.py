from abc import ABC, abstractmethod
from numbers import Number
from typing import Iterable, Optional, Union

from docplex.mp.dvar import Var
from docplex.mp.model import Model

from socratic.op import Logic, Formula


class FloatInterval(ABC):
    def __init__(self, lower: float, upper: float):
        """A base class for closed and open intervals defined by their lower and upper bounds.

        :param lower: The interval's minimum or infimum value if open.
        :param upper: The interval's maximum or supremum value if open.
        """
        self.lower = lower
        self.upper = upper

    @abstractmethod
    def configure(self, m: Model, gap: Var, val: Var, active: Var):
        """Add constraints to a model requiring a value to lie within the represented interval (if active).

        :param m: An MP model containing gap, val, and active to which constraints will be added.
        :param gap: The model's gap variable, used to enforce strict inequality.
        :param val: The continuous variable to be constrained within the interval.
        :param active: A boolean variable indicating whether added constraints are active.
        """
        pass

    @abstractmethod
    def compliment(self, m: Model, gap: Var, val: Var, active: Var):
        """Add constraints to a model requiring a value to lie outside the represented interval.

        :param m: An MP model containing gap, val, and active to which constraints will be added.
        :param gap: The model's gap variable, used to enforce strict inequality.
        :param val: The continuous variable to be constrained outside the interval.
        :param active: A boolean variable indicating which side of the interval val lies beyond.
        """
        pass


class ClosedInterval(FloatInterval):
    """An interval that includes both its lower and upper bound values.
    """

    def configure(self, m, gap, val, active):
        m.add_indicator(active, val >= self.lower)
        m.add_indicator(active, val <= self.upper)

    def compliment(self, m, gap, val, active):
        m.add_indicator(active, val <= self.lower - gap)
        m.add_indicator(active, val >= self.upper + gap, 0)


class Point(ClosedInterval):
    def __init__(self, point):
        """A point interval with equal lower and upper bound.

        :param point: The singular value within the interval.
        """
        super().__init__(point, point)


class AtLeast(ClosedInterval):
    def __init__(self, lower):
        """An interval containing all points greater than or equal to its lower bound.

        :param lower: The interval's min value.
        """
        super().__init__(lower, 1)


class AtMost(ClosedInterval):
    def __init__(self, upper):
        """An interval containing all points less than or equal to its upper bound.

        :param upper: The interval's max value.
        """
        super().__init__(0, upper)


class OpenInterval(FloatInterval):
    """An interval that excludes both its lower and upper bound values.
    """

    def configure(self, m, gap, val, active):
        m.add_indicator(active, val >= self.lower + gap)
        m.add_indicator(active, val <= self.upper - gap)

    def compliment(self, m, gap, val, active):
        m.add_indicator(active, val <= self.lower)
        m.add_indicator(active, val >= self.upper, 0)


class OpenLowerInterval(FloatInterval):
    """An interval that excludes its lower bound value but includes its upper bound value.
    """

    def configure(self, m, gap, val, active):
        m.add_indicator(active, val >= self.lower + gap)
        m.add_indicator(active, val <= self.upper)

    def compliment(self, m, gap, val, active):
        m.add_indicator(active, val <= self.lower)
        m.add_indicator(active, val >= self.upper + gap, 0)


class GreaterThan(OpenLowerInterval):
    def __init__(self, lower):
        """An interval containing all points strictly greater than its lower bound.

        :param lower: The interval's infimum.
        """
        super().__init__(lower, 1)


class OpenUpperInterval(FloatInterval):
    """An interval that includes its lower bound value but excludes its upper bound value.
    """

    def configure(self, m, gap, val, active):
        m.add_indicator(active, val >= self.lower)
        m.add_indicator(active, val <= self.upper - gap)

    def compliment(self, m, gap, val, active):
        m.add_indicator(active, val <= self.lower - gap)
        m.add_indicator(active, val >= self.upper, 0)


class LessThan(OpenUpperInterval):
    def __init__(self, upper):
        """An interval containing all points strictly less than its upper bound.

        :param upper: The interval's supremum.
        """
        super().__init__(0, upper)


class Sentence(ABC):
    """A base class to associate collections of formulae with sets of possible truth values.
    """
    pass


class SimpleSentence(Sentence):
    TruthType = Union[FloatInterval, Number]

    def __init__(self, formula: Formula, intervals: Union[Iterable[TruthType], TruthType]):
        """A sentence made up of one formula and a union of intervals of possible truth values.

        :param formula: A logical expression.
        :param intervals: A collection of intervals representing the formula's set of possible truth values.  Numbers
            provided in lieu of FloatIntervals are coerced into Points.  In addition, one may provide an individual
            FloatInterval or Number in lieu of an Iterable to effect a single-element union.
        """
        if not isinstance(intervals, Iterable):
            intervals = [intervals]

        self.formula = formula
        self.intervals = [Point(r) if isinstance(r, Number) else r for r in intervals]

    def reset(self):
        """Erase any previous configuration in preparation for reconfiguration.
        """
        self.formula.reset()

    def configure(self, m: Model, gap: Var, logic: Logic):
        """Add constraints to a model defining the formula to have truth value lying within any associated interval.

        :param m: An MP model containing gap to which the formula and intervals will be added.
        :param gap: The model's gap variable, used to enforce strict inequality.
        :param logic: The t-norm used to define the sentence's connectives.
        """
        self.formula.configure(m, gap, logic)

        active_interval = m.binary_var_list(len(self.intervals), name=repr(self.formula) + ".active_interval")
        m.add_constraint(m.sum(active_interval) == 1)
        for i in range(len(self.intervals)):
            self.intervals[i].configure(m, gap, self.formula.val, active_interval[i])

    def compliment(self, m: Model, gap: Var, logic: Logic):
        """Add constraints to a model defining the formula to have truth value lying outside all associated intervals.

        :param m: An MP model containing gap to which the formula and intervals will be added.
        :param gap: The model's gap variable, used to enforce strict inequality.
        :param logic: The t-norm used to define the sentence's connectives.
        """
        self.formula.configure(m, gap, logic)

        active_interval = m.binary_var_list(len(self.intervals), name=repr(self.formula) + ".active_interval")
        for i in range(len(self.intervals)):
            self.intervals[i].compliment(m, gap, self.formula.val, active_interval[i])


class Theory(object):
    def __init__(self, *args: Union[SimpleSentence, Formula]):
        """A collection of sentences for testing mutual satisfiability and/or entailment.

        :param args: The theory's sentences.  Formulae provided in lieu of Sentences are coerced into SimpleSentences
            with truth value exactly 1.
        """
        self.sentences = [SimpleSentence(s, 1) if isinstance(s, Formula) else s for s in args]

        self.m = None
        self.gap = None

    def satisfiable(self, logic=Logic.LUKASIEWICZ):
        """Test whether a theory's sentences may all be true simultaneously.

        :param logic: The t-norm used to define the sentences' connectives.
        :return: True iff the theory is satisfiable.  Also, upon completion, Theory attributes m and gap and all
            variables and constraints created for intervals and formulae remain available for inspection.
        """
        return not self.entails(None, logic)

    def entails(self, query: Optional[Union[SimpleSentence, Formula]], logic=Logic.LUKASIEWICZ):
        """Test whether a query sentence must be true whenever a theory's sentences are all true.

        :param query: The sentence to be tested or None if testing satisfiability.
        :param logic: The t-norm used to define the sentences' connectives.
        :return: True iff the theory entails the query.  Also, upon completion, Theory attributes m and gap and all
            variables and constraints created for intervals and formulae remain available for inspection.
        """
        if isinstance(query, Formula):
            query = SimpleSentence(query, 1)

        self.m = Model(cts_by_name=True)
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
