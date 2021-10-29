from abc import ABC, abstractmethod
from enum import Enum
from numbers import Real


class Logic(Enum):
    GODEL = 0
    LUKASIEWICZ = 1


class Formula(ABC):
    def __init__(self):
        self.val = float("nan")

    def __rmul__(self, other):
        return Coef(other, self)

    __mul__ = __rmul__

    def __truediv__(self, other):
        return Coef(1 / other, self)

    def __pow__(self, other):
        return Exp(other, self)

    def reset(self):
        if self.val is not None:
            self.val = None

            return True

    def configure(self, m, gap, logic):
        if self.val is None:
            var_name = repr(self) + ".val"
            self.val = m.get_var_by_name(var_name)

            if self.val is None:
                self.val = m.continuous_var(lb=0, ub=1, name=var_name)

            return True


class Prop(Formula):
    def __init__(self, name):
        super().__init__()

        self.name = name

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other

        return type(self) is type(other) and self.name == other.name

    def __hash__(self):
        return super().__hash__()

    def __repr__(self, _depth=0):
        return f"{type(self).__name__}({repr(self.name)})"

    def __str__(self, _depth=0):
        return str(self.name)


class Const(Formula):
    def __init__(self, val):
        super().__init__()

        self.val = val

    def __eq__(self, other):
        if isinstance(other, Real):
            return self.val == other

        return type(self) is type(other) and self.val == other.val

    def __hash__(self):
        return super().__hash__()

    def __repr__(self, _depth=0):
        return f"{type(self).__name__}({repr(self.val)})"

    def __str__(self, _depth=0):
        return str(self.val)

    def reset(self):
        pass

    def configure(self, m, gap, logic):
        pass


class Operator(Formula, ABC):
    @property
    @abstractmethod
    def symb(self): pass

    def __init__(self, *args, logic=None):
        super().__init__()

        self.logic = logic

        def init_operand(arg):
            if isinstance(arg, str):
                return Prop(arg)

            if isinstance(arg, Real):
                return Const(arg)

            return arg

        self.operands = [init_operand(arg) for arg in args]

    def __eq__(self, other):
        return (type(self) is type(other) and
                self.logic is other.logic and
                self.operands == other.operands)

    def __hash__(self):
        return super().__hash__()

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

    def _annotate_recurrence(self, fn, depth):
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
    def _add_constraints(self, m, gap, logic):
        pass

    def _add_constraint(self, m, constraint, name="constraint"):
        ct_name = f"{repr(self)}.{name}"
        if m.get_constraint_by_name(ct_name) is None:
            return m.add_constraint(constraint, ctname=ct_name)


class And(Operator):
    @property
    def symb(self): return '⊗'

    def _add_constraints(self, m, gap, logic):
        if logic is Logic.GODEL:
            self._add_constraint(m, self.val == m.min(op.val for op in self.operands))

        else:  # logic is Logic.LUKASIEWICZ
            self._add_constraint(m, self.val == m.max(0, 1 - m.sum(1 - op.val for op in self.operands)))


class WeakAnd(And):
    @property
    def symb(self): return '∧'

    def __init__(self, *args):
        super().__init__(*args)

    def _add_constraints(self, m, gap, logic):
        super()._add_constraints(m, gap, Logic.GODEL)


class Or(Operator):
    @property
    def symb(self): return '⊕'

    def _add_constraints(self, m, gap, logic):
        if logic is Logic.GODEL:
            self._add_constraint(m, self.val == m.max(op.val for op in self.operands))

        else:  # logic is Logic.LUKASIEWICZ
            self._add_constraint(m, self.val == m.min(1, m.sum(op.val for op in self.operands)))


class WeakOr(Or):
    @property
    def symb(self): return '∨'

    def __init__(self, *args):
        super().__init__(*args)

    def _add_constraints(self, m, gap, logic):
        super()._add_constraints(m, gap, Logic.GODEL)


class BinaryOperator(Operator, ABC):
    def __init__(self, lhs, rhs, logic=None):
        super().__init__(lhs, rhs, logic=logic)

    @property
    def lhs(self): return self.operands[0]

    @lhs.setter
    def lhs(self, value): self.operands[0] = value

    @property
    def rhs(self): return self.operands[1]

    @rhs.setter
    def rhs(self, value): self.operands[1] = value


class Implies(BinaryOperator):
    @property
    def symb(self): return '→'

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
                self._add_constraint(m, self.val == 1 - self.lhs.val)
            else:
                self._add_constraint(m, self.val == m.min(1, 1 - self.lhs.val + self.rhs.val))


class Equiv(BinaryOperator):
    @property
    def symb(self): return '↔'

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
            self._add_constraint(m, self.val == 1 - m.abs(self.lhs.val - self.rhs.val))


class UnaryOperator(Operator, ABC):
    def __init__(self, arg, logic=None):
        super().__init__(arg, logic=logic)

    @property
    def arg(self): return self.operands[0]

    @arg.setter
    def arg(self, value): self.operands[0] = value

    def __str__(self, _depth=0):
        return self._annotate_recurrence(
            lambda d: self.symb + self.arg.__str__(d),
            _depth)


class Not(UnaryOperator):
    @property
    def symb(self): return '¬'

    def _add_constraints(self, m, gap, logic):
        impl = Implies(self.arg, 0, logic=logic)
        impl.val = self.val
        impl._add_constraints(m, gap, logic)


class Inv(Not):
    @property
    def symb(self): return '∼'

    def __init__(self, arg):
        super().__init__(arg)

    def _add_constraints(self, m, gap, logic):
        super()._add_constraints(m, gap, Logic.LUKASIEWICZ)


class Delta(UnaryOperator):
    @property
    def symb(self): return '△'

    def __init__(self, arg):
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

    def __init__(self, coef, arg):
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
        self._add_constraint(m, self.val == m.min(1, self.coef * self.arg.val))


class Exp(UnaryOperator):
    @property
    def symb(self): return '^'

    def __init__(self, exp, arg):
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
        self._add_constraint(m, self.val == m.max(0, 1 - self.exp * (1 - self.arg.val)))
