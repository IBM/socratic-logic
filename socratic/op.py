from collections.abc import Iterable
from enum import Enum
from numbers import Number


class Logic(Enum):
    GODEL = 0
    LUKASIEWICZ = 1


class Formula(object):
    def __init__(self):
        self.val = float("nan")

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

    def __repr__(self):
        return f"{type(self).__name__}({repr(self.name)})"

    def __str__(self):
        return str(self.name)


class Constant(Formula):
    def __init__(self, val):
        super().__init__()

        self.val = val

    def __repr__(self):
        return f"{type(self).__name__}({repr(self.val)})"

    def __str__(self):
        return str(self.val)

    def reset(self):
        pass

    def configure(self, m, gap, logic):
        pass


class Operator(Formula):
    @property
    def symb(self): return '_'

    def __init__(self, *args, logic=None):
        super().__init__()

        self.logic = logic

        if len(args) == 1 and isinstance(args[0], Iterable):
            if not isinstance(args[0], str):
                args = args[0]

        def init_operand(arg):
            if isinstance(arg, str):
                return Prop(arg)

            if isinstance(arg, Number):
                return Constant(arg)

            return arg

        self.operands = [init_operand(arg) for arg in args]

    def __repr__(self):
        logic_arg = [f"logic={self.logic}"] if self.logic is not None else []
        arg_repr = ", ".join(list(map(repr, self.operands)) + logic_arg)
        return f"{type(self).__name__}({arg_repr})"

    def __str__(self):
        return "(%s)" % f" {self.symb} ".join(map(str, self.operands))

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
            self.add_constraints(m, gap, logic)

    def add_constraints(self, m, gap, logic):
        pass

    def add_constraint(self, m, constraint, name="constraint"):
        ct_name = f"{repr(self)}.{name}"
        if m.get_constraint_by_name(ct_name) is None:
            return m.add_constraint(constraint, ctname=ct_name)


class And(Operator):
    @property
    def symb(self): return '⊗'

    def add_constraints(self, m, gap, logic):
        if logic is Logic.GODEL:
            self.add_constraint(m, self.val == m.min(op.val for op in self.operands))

        else:  # logic is Logic.LUKASIEWICZ
            self.add_constraint(m, self.val == m.max(0, 1 - m.sum(1 - op.val for op in self.operands)))


class WeakAnd(And):
    @property
    def symb(self): return '∧'

    def __init__(self, *args):
        super().__init__(*args)

    def add_constraints(self, m, gap, logic):
        super().add_constraints(m, gap, Logic.GODEL)


class Or(Operator):
    @property
    def symb(self): return '⊕'

    def add_constraints(self, m, gap, logic):
        if logic is Logic.GODEL:
            self.add_constraint(m, self.val == m.max(op.val for op in self.operands))

        else:  # logic is Logic.LUKASIEWICZ
            self.add_constraint(m, self.val == m.min(1, m.sum(op.val for op in self.operands)))


class WeakOr(Or):
    @property
    def symb(self): return '∨'

    def __init__(self, *args):
        super().__init__(*args)

    def add_constraints(self, m, gap, logic):
        super().add_constraints(m, gap, Logic.GODEL)


class Implies(Operator):
    @property
    def symb(self): return '→'

    def __init__(self, lhs, rhs, logic=None):
        super().__init__(lhs, rhs, logic=logic)

        self.lhs = self.operands[0]
        self.rhs = self.operands[1]

    def add_constraints(self, m, gap, logic):
        if logic is Logic.GODEL:
            var_name = repr(self) + ".lhs_le_rhs"
            if m.get_var_by_name(var_name) is None:
                lhs_le_rhs = m.binary_var(name=var_name)

                m.add_indicator(lhs_le_rhs, self.lhs.val <= self.rhs.val)
                m.add_indicator(lhs_le_rhs, self.val == 1)

                m.add_indicator(lhs_le_rhs, self.lhs.val >= self.rhs.val + gap, 0)
                m.add_indicator(lhs_le_rhs, self.val == self.rhs.val, 0)

        else:  # logic is Logic.LUKASIEWICZ
            if isinstance(self.rhs.val, Number) and self.rhs.val == 0:
                self.add_constraint(m, self.val == 1 - self.lhs.val)
            else:
                self.add_constraint(m, self.val == m.min(1, 1 - self.lhs.val + self.rhs.val))


class Not(Implies):
    @property
    def symb(self): return '¬'

    def __init__(self, arg, logic=None):
        super().__init__(arg, 0, logic=logic)

        self.operands = self.operands[:1]
        self.arg = self.operands[0]

    def __str__(self):
        return self.symb + str(self.arg)


class Inv(Not):
    @property
    def symb(self): return '∼'

    def __init__(self, arg):
        super().__init__(arg)

    def add_constraints(self, m, gap, logic):
        super().add_constraints(m, gap, Logic.LUKASIEWICZ)


class Equiv(Operator):
    @property
    def symb(self): return '↔'

    def __init__(self, lhs, rhs, logic=None):
        super().__init__(lhs, rhs, logic=logic)

        self.lhs = self.operands[0]
        self.rhs = self.operands[1]

    def add_constraints(self, m, gap, logic):
        if logic is Logic.GODEL:
            var_name = repr(self) + ".lhs_eq_rhs"
            if m.get_var_by_name(var_name) is None:
                lhs_eq_rhs = m.binary_var(name=var_name)

                m.add_indicator(lhs_eq_rhs, self.lhs.val == self.rhs.val)
                m.add_indicator(lhs_eq_rhs, self.val == 1)

                m.add_indicator(lhs_eq_rhs, m.abs(self.lhs.val - self.rhs.val) >= gap, 0)
                m.add_indicator(lhs_eq_rhs, self.val == m.min(self.lhs.val, self.rhs.val), 0)

        else:  # logic is Logic.LUKASIEWICZ
            self.add_constraint(m, self.val == 1 - m.abs(self.lhs.val - self.rhs.val))


class Delta(Operator):
    @property
    def symb(self): return '△'

    def __init__(self, arg):
        super().__init__(arg)

        self.arg = self.operands[0]

    def __str__(self):
        return self.symb + str(self.arg)

    def add_constraints(self, m, gap, logic):
        var_name = repr(self) + ".arg_eq_one"
        if m.get_var_by_name(var_name) is None:
            arg_eq_one = m.binary_var(name=var_name)

            m.add_indicator(arg_eq_one, self.arg.val == 1)
            m.add_indicator(arg_eq_one, self.val == 1)

            m.add_indicator(arg_eq_one, self.arg.val <= 1 - gap, 0)
            m.add_indicator(arg_eq_one, self.val == 0, 0)
