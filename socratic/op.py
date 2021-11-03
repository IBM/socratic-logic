from abc import ABC, abstractmethod
from enum import Enum
from numbers import Real
from typing import Callable, Optional, Union

from docplex.mp.constr import AbstractConstraint
from docplex.mp.dvar import Var
from docplex.mp.model import Model


class Logic(Enum):
    GODEL = 0
    LUKASIEWICZ = 1


class Formula(ABC):
    val: Union[Var, Real, None]

    def __init__(self):
        """A base class for symbolic logical expressions.
        """
        self.val = float("nan")

    def __rmul__(self, other: Real):
        """Create a Coef with infix multiplication.

        >>> 3 * Prop('a')
        Coef(3, Prop('a'))

        :param other: The scalar coefficient.
        :return: A Coef object referring to this object by reference.
        """
        return Coef(other, self)

    __mul__ = __rmul__

    def __truediv__(self, other: Real):
        """Create a Coef with infix division.

        >>> Prop('a') / 2
        Coef(0.5, Prop('a'))

        :param other: The scalar divisor.
        :return: A Coef object referring to this object by reference.
        """
        return Coef(1 / other, self)

    def __pow__(self, other: Real):
        """Create an Exp with infix exponentiation.

        >>> Prop('a') ** 1.5
        Exp(1.5, Prop('a'))

        :param other: The scalar exponent.
        :return: An Exp object referring to this object by reference.
        """
        return Exp(other, self)

    def __eq__(self, other):
        """Test if two formulae have equal structure.

        :param other: Another formula.
        :return: True iff other.configure would yield exactly the same set of constraints and variables.
        """
        return type(self) == type(other) and repr(self) == repr(other)

    @abstractmethod
    def __repr__(self, _depth=0):
        """Return a code-like string to reconstruct a formula while avoiding cycles.

        Any subformula referring to its own ancestor is replaced with a number of ``.`` characters equal to the number
        of formulae between the subformula and ancestor, inclusive, such that, e.g., ``..`` refers to the immediately
        enclosing expression, ``...`` to the expression enclosing that, and so forth.

        >>> repr(Implies('a', Implies('b', 'a')))
        "Implies(Prop('a'), Implies(Prop('b'), Prop('a')))"

        >>> f = Or()
        >>> f.operands = [f, Not(f)]
        >>> repr(f)
        'Or(.., Not(...))'

        :param _depth: Not intended to be set by the user: a protected argument permitting the unique representation of
            cyclic structures.
        """
        pass

    @abstractmethod
    def __str__(self, _depth=0):
        """Return a human-readable string detailing a formula while avoiding cycles.

        Subformulae referring to their own ancestors are handled similarly to repr.

        >>> str(Implies('a', Implies('b', 'a')))
        '(a → (b → a))'

        >>> str(Or(Not('a'), Not('b'), 'c'))
        '(¬a ⊕ ¬b ⊕ c)'

        :param _depth: Not intended to be set by the user: a protected argument permitting the unique representation of
            cyclic structures.
        """
        pass

    def reset(self):
        """Erase any previous configuration in preparation for reconfiguration.

        :return: True if subformulae also need to be reset (i.e., are not cyclical).
        """
        if self.val is not None:
            self.val = None

            return True

    def configure(self, m: Model, gap: Var, logic: Logic):
        """Recursively add constraints and variables defining the formula to a model.

        :param m: An MP model containing gap to which the formula will be added.
        :param gap: The model's gap variable, used to enforce strict inequality.
        :param logic: The t-norm used to define the formula's connectives unless explicitly overridden by an operator's
            logic argument.
        :return: True if subformulae also need to be configured (i.e., are not cyclical).
        """
        if self.val is None:
            var_name = repr(self) + ".val"
            self.val = m.get_var_by_name(var_name)

            if self.val is None:
                self.val = m.continuous_var(lb=0, ub=1, name=var_name)

            return True


class Prop(Formula):
    def __init__(self, name: str):
        """A logical propositional variable to which may be assigned an individual truth value.

        :param name: A string identifying the proposition everywhere it occurs in a theory.  Distinct Prop objects that
            nonetheless share a name compare equal and will be associated with the same variable in the MP model.
        """
        super().__init__()

        self.name = name

    def __repr__(self, _depth=0):
        return f"{type(self).__name__}({repr(self.name)})"

    def __str__(self, _depth=0):
        return str(self.name)


class Const(Formula):
    def __init__(self, val: Real):
        """A fixed truth value constant for use in constructing logical expressions.

        :param val: The constant's given value.
        """
        super().__init__()

        self.val = val

    def __repr__(self, _depth=0):
        return f"{type(self).__name__}({repr(self.val)})"

    def __str__(self, _depth=0):
        return str(self.val)

    def reset(self):
        pass

    def configure(self, m, gap, logic):
        pass


SubformulaType = Union[Formula, str, Real]


class Operator(Formula, ABC):
    @property
    @abstractmethod
    def symb(self) -> str:
        """The operator's symbol as emitted by str.
        """
        pass

    def __init__(self, *args: SubformulaType, logic: Optional[Logic] = None):
        """A base class for operators used to build more complex formulae out of component subformulae.

        :param args: The operator's operands.
        :param logic: The t-norm used to define the operator or None to permit later specification by Formula.configure.
        """
        super().__init__()

        self.logic = logic

        def init_operand(arg: SubformulaType) -> Formula:
            if isinstance(arg, str):
                return Prop(arg)

            if isinstance(arg, Real):
                return Const(arg)

            return arg

        self.operands = [init_operand(arg) for arg in args]

    def __repr__(self, _depth=0):
        def fn(d):
            logic_arg = [f"logic={self.logic}"] if self.logic is not None else []
            arg_repr = ", ".join([op.__repr__(d) for op in self.operands] + logic_arg)
            return f"{type(self).__name__}({arg_repr})"

        return self._annotate_recurrence(fn, _depth)

    def __str__(self, _depth=0):
        def fn(d):
            fmt = f"({self.symb}%s)" if len(self.operands) <= 1 else "(%s)"
            return fmt % f" {self.symb} ".join(op.__str__(d) for op in self.operands)

        return self._annotate_recurrence(fn, _depth)

    def _annotate_recurrence(self, fn: Callable[[int], str], depth: int):
        """A helper function used to prevent infinite recursion on cyclic formulae.

        :param fn: A function called if the formula is acyclic (so far).  Should recursively call _annotate_recurrence.
        :param depth: The current number of recursions.
        :return: The result of fn or a string indicating recurrence to have occurred.
        """
        if hasattr(self, "_depth"):
            return '.' * (depth - self._depth + 1)
        self._depth = depth
        try:
            return fn(depth + 1)
        finally:
            del self._depth

    def reset(self):
        if super().reset():
            for op in self.operands:
                op.reset()

    def configure(self, m, gap, logic):
        if super().configure(m, gap, logic):
            for op in self.operands:
                op.configure(m, gap, logic)

            if self.logic is not None:
                logic = self.logic
            self._add_constraints(m, gap, logic)

    @abstractmethod
    def _add_constraints(self, m: Model, gap: Var, logic: Logic):
        """Add constraints and variables defining the specific operator to a model.

        :param m: An MP model containing gap to which the operator will be added.
        :param gap: The model's gap variable, used to enforce strict inequality.
        :param logic: The t-norm used to define the operator.
        """
        pass

    def _add_constraint(self, m: Model, ct: Callable[[], AbstractConstraint], name="constraint"):
        """A helper function used to avoid adding redundant constraints.

        :param m: An MP model to which the constraint will be added.
        :param ct: A function returning the constraint in question.
        :param name: A suffix used to distinguish multiple constraints added for the same operator.
        :return: The result of Model.add_constraint or None if not added.
        """
        ct_name = f"{repr(self)}.{name}"
        if m.get_constraint_by_name(ct_name) is None:
            return m.add_constraint(ct(), ctname=ct_name)


class And(Operator):
    @property
    def symb(self):
        return '⊗'

    def __init__(self, *args, logic=None):
        """Strong conjunction as evaluated via the t-norm.

        :param args: The conjunction's operands.
        :param logic: Whether to compute LUKASIEWICZ logic's max(0, 1 - sum(1 - ops)) or GODEL logic's min(ops), or None
            to permit later specification by Formula.configure.
        """
        super().__init__(*args, logic=logic)

    def _add_constraints(self, m, gap, logic):
        if logic is Logic.GODEL:
            self._add_constraint(m, lambda: self.val == m.min(op.val for op in self.operands))

        else:  # logic is Logic.LUKASIEWICZ
            self._add_constraint(m, lambda: self.val == m.max(0, 1 - m.sum(1 - op.val for op in self.operands)))


class WeakAnd(And):
    @property
    def symb(self): return '∧'

    def __init__(self, *args):
        """Weak conjunction, always evaluated as min.

        :param args: The conjunction's operands.
        """
        super().__init__(*args)

    def _add_constraints(self, m, gap, logic):
        super()._add_constraints(m, gap, Logic.GODEL)


class Or(Operator):
    @property
    def symb(self):
        return '⊕'

    def __init__(self, *args, logic=None):
        """Strong disjunction as evaluated via the t-conorm.

        :param args: The disjunction's operands.
        :param logic: Whether to compute LUKASIEWICZ logic's min(1, sum(ops)) or GODEL logic's max(ops), or None to
            permit later specification by Formula.configure.
        """
        super().__init__(*args, logic=logic)

    def _add_constraints(self, m, gap, logic):
        if logic is Logic.GODEL:
            self._add_constraint(m, lambda: self.val == m.max(op.val for op in self.operands))

        else:  # logic is Logic.LUKASIEWICZ
            self._add_constraint(m, lambda: self.val == m.min(1, m.sum(op.val for op in self.operands)))


class WeakOr(Or):
    @property
    def symb(self): return '∨'

    def __init__(self, *args):
        """Weak disjunction, always evaluated as max.

        :param args: The disjunction's operands.
        """
        super().__init__(*args)

    def _add_constraints(self, m, gap, logic):
        super()._add_constraints(m, gap, Logic.GODEL)


class BinaryOperator(Operator, ABC):
    def __init__(self, lhs: SubformulaType, rhs: SubformulaType, logic=None):
        """A base class for operators accepting exactly two operands.

        :param lhs: The operator's left-hand side.
        :param rhs: The operator's right-hand side.
        :param logic: The t-norm used to define the operator or None to permit later specification by Formula.configure.
        """
        super().__init__(lhs, rhs, logic=logic)

    @property
    def lhs(self):
        """Get or set the operator's first operand.
        """
        return self.operands[0]

    @lhs.setter
    def lhs(self, value: Formula):
        self.operands[0] = value

    @property
    def rhs(self):
        """Get or set the operator's second operand.
        """
        return self.operands[1]

    @rhs.setter
    def rhs(self, value: Formula):
        self.operands[1] = value


class Implies(BinaryOperator):
    @property
    def symb(self):
        return '→'

    def __init__(self, lhs, rhs, logic=None):
        """Logical implication as evaluated via the residuum of the t-norm.

        :param lhs: The implication's antecedent.
        :param rhs: The implication's consequent.
        :param logic: Whether to compute LUKASIEWICZ logic's min(1, 1 - lhs + rhs) or GODEL logic's 1 if lhs <= rhs else
            rhs, or None to permit later specification by Formula.configure.
        """
        super().__init__(lhs, rhs, logic=logic)

    def _add_constraints(self, m, gap, logic):
        if logic is Logic.GODEL:
            var_name = repr(self) + ".lhs_le_rhs"
            if m.get_var_by_name(var_name) is None:
                lhs_le_rhs = m.binary_var(name=var_name)

                m.add_indicator(lhs_le_rhs, self.lhs.val <= self.rhs.val)
                m.add_indicator(lhs_le_rhs, self.val == 1)

                m.add_indicator(lhs_le_rhs, self.lhs.val >= self.rhs.val + gap, 0)
                m.add_indicator(lhs_le_rhs, self.val == self.rhs.val, 0)

        else:  # logic is Logic.LUKASIEWICZ
            if isinstance(self.rhs.val, Real) and self.rhs.val == 0:
                self._add_constraint(m, lambda: self.val == 1 - self.lhs.val)
            else:
                self._add_constraint(m, lambda: self.val == m.min(1, 1 - self.lhs.val + self.rhs.val))


class Equiv(BinaryOperator):
    @property
    def symb(self):
        return '↔'

    def __init__(self, lhs, rhs, logic=None):
        """Logical equivalence, evaluated (lhs → rhs) ⊗ (rhs → lhs).

        :param lhs: The equivalence's left-hand side.
        :param rhs: The equivalence's right-hand side.
        :param logic: Whether to compute LUKASIEWICZ logic's 1 - abs(lhs - rhs) or GODEL logic's 1 if lhs == rhs else
            min(lhs, rhs), or None to permit later specification by Formula.configure.
        """
        super().__init__(lhs, rhs, logic=logic)

    def _add_constraints(self, m, gap, logic):
        if logic is Logic.GODEL:
            var_name = repr(self) + ".lhs_eq_rhs"
            if m.get_var_by_name(var_name) is None:
                lhs_eq_rhs = m.binary_var(name=var_name)

                m.add_indicator(lhs_eq_rhs, self.lhs.val == self.rhs.val)
                m.add_indicator(lhs_eq_rhs, self.val == 1)

                m.add_indicator(lhs_eq_rhs, m.abs(self.lhs.val - self.rhs.val) >= gap, 0)
                m.add_indicator(lhs_eq_rhs, self.val == m.min(self.lhs.val, self.rhs.val), 0)

        else:  # logic is Logic.LUKASIEWICZ
            self._add_constraint(m, lambda: self.val == 1 - m.abs(self.lhs.val - self.rhs.val))


class UnaryOperator(Operator, ABC):
    def __init__(self, arg: SubformulaType, logic=None):
        """A base class for operators accepting exactly one operand.

        :param arg: The operator's single operand.
        :param logic: The t-norm used to define the operator or None to permit later specification by Formula.configure.
        """
        super().__init__(arg, logic=logic)

    @property
    def arg(self):
        """Get or set the operator's single operand.
        """
        return self.operands[0]

    @arg.setter
    def arg(self, value: Formula):
        self.operands[0] = value

    def __str__(self, _depth=0):
        return self._annotate_recurrence(
            lambda d: self.symb + self.arg.__str__(d),
            _depth)


class Not(UnaryOperator):
    @property
    def symb(self): return '¬'

    def __init__(self, arg, logic=None):
        """Logical negation, evaluated arg → 0.

        :param arg: The negated expression.
        :param logic: Whether to compute LUKASIEWICZ logic's 1 - arg or GODEL logic's 1 if lhs == 0 else 0, or None to
            permit later specification by Formula.configure.
        """
        super().__init__(arg, logic=logic)

    def _add_constraints(self, m, gap, logic):
        impl = Implies(self.arg, 0, logic=logic)
        impl.val = self.val
        impl._add_constraints(m, gap, logic)


class Inv(Not):
    @property
    def symb(self): return '∼'

    def __init__(self, arg):
        """Involute negation, always evaluated 1 - arg.

        :param arg: The negated expression.
        """
        super().__init__(arg)

    def _add_constraints(self, m, gap, logic):
        super()._add_constraints(m, gap, Logic.LUKASIEWICZ)


class Delta(UnaryOperator):
    @property
    def symb(self): return '△'

    def __init__(self, arg):
        """Upward triangle, similar to model logic's necessity, evaluated 1 if arg == 1 else 0.

        :param arg: The necessary expression.
        """
        super().__init__(arg)

    def _add_constraints(self, m, gap, logic):
        var_name = repr(self) + ".arg_eq_one"
        if m.get_var_by_name(var_name) is None:
            arg_eq_one = m.binary_var(name=var_name)

            m.add_indicator(arg_eq_one, self.arg.val == 1)
            m.add_indicator(arg_eq_one, self.val == 1)

            m.add_indicator(arg_eq_one, self.arg.val <= 1 - gap, 0)
            m.add_indicator(arg_eq_one, self.val == 0, 0)


class Nabla(UnaryOperator):
    @property
    def symb(self): return '▽'

    def __init__(self, arg):
        """Downward triangle, similar to model logic's possibility, evaluated 1 if arg > 0 else 0.

        :param arg: The possible expression.
        """
        super().__init__(arg)

    def _add_constraints(self, m, gap, logic):
        var_name = repr(self) + ".arg_eq_zero"
        if m.get_var_by_name(var_name) is None:
            arg_eq_zero = m.binary_var(name=var_name)

            m.add_indicator(arg_eq_zero, self.arg.val == 0)
            m.add_indicator(arg_eq_zero, self.val == 0)

            m.add_indicator(arg_eq_zero, self.arg.val >= gap, 0)
            m.add_indicator(arg_eq_zero, self.val == 1, 0)


class Coef(UnaryOperator):
    @property
    def symb(self): return '⋅'

    def __init__(self, coef: Real, arg):
        """Or-like weighting via scalar coefficient, evaluated min(1, coef * arg).

        :param coef: The scalar coefficient.
        :param arg: The scaled expression.
        """
        super().__init__(arg)

        self.coef = coef

    def __repr__(self, _depth=0):
        return self._annotate_recurrence(
            lambda d: f"{type(self).__name__}({repr(self.coef)}, {self.arg.__repr__(d)})",
            _depth)

    def __str__(self, _depth=0):
        return self._annotate_recurrence(
            lambda d: str(self.coef) + self.symb + self.arg.__str__(d),
            _depth)

    def _add_constraints(self, m, gap, logic):
        self._add_constraint(m, lambda: self.val == m.min(1, self.coef * self.arg.val))


class Exp(UnaryOperator):
    @property
    def symb(self): return '^'

    def __init__(self, exp: Real, arg):
        """And-like weighting via scalar exponent, evaluated min(0, 1 - exp * (1 - arg)).

        :param exp: The scalar exponent.
        :param arg: The scaled expression.
        """
        super().__init__(arg)

        self.exp = exp

    def __repr__(self, _depth=0):
        return self._annotate_recurrence(
            lambda d: f"{type(self).__name__}({repr(self.exp)}, {self.arg.__repr__(d)})",
            _depth)

    def __str__(self, _depth=0):
        def fn(d):
            fmt = "(%s)%s%s" if isinstance(self.arg, UnaryOperator) else "%s%s%s"
            return fmt % (self.arg.__str__(d), self.symb, self.exp)

        return self._annotate_recurrence(fn, _depth)

    def _add_constraints(self, m, gap, logic):
        self._add_constraint(m, lambda: self.val == m.max(0, 1 - self.exp * (1 - self.arg.val)))
