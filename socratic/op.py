from collections.abc import Iterable
from enum import Enum
from numbers import Number


class Logic(Enum):
    GODEL = 0
    LUKASIEWICZ = 1


class Formula(object):
    def __init__(self):
        self.val = "unconfigured"

    def configure(self, m, gap, logic):
        if self.val is None:
            self.val = m.continuous_var(lb=0, ub=1, name=str(self))

            return True

    def reset(self):
        if self.val is not None:
            self.val = None

            return True


class Prop(Formula):
    def __init__(self, name):
        super().__init__()

        self.name = name

    def __str__(self):
        return str(self.name)


class Constant(Formula):
    def __init__(self, val):
        super().__init__()

        self.val = val

    def __str__(self):
        return str(self.val)

    def configure(self, m, gap, logic):
        pass

    def reset(self):
        pass


class Operator(Formula):
    def __init__(self, *args, logic=None):
        super().__init__()

        self.logic = logic

        if len(args) == 1 and isinstance(args[0], Iterable):
            args = args[0]

        self.operands = [Constant(arg) if isinstance(arg, Number) else arg for arg in args]

    def __str__(self):
        logic_arg = ["logic=%s" % str(self.logic)] if self.logic is not None else []
        return "%s(%s)" % (type(self).__name__, ", ".join(map(str, self.operands + logic_arg)))

    def configure(self, m, gap, logic):
        if super().configure(m, gap, logic):
            for operand in self.operands:
                operand.configure(m, gap, logic)

            self.add_constraint(m, gap, logic)

    def add_constraint(self, m, gap, logic):
        pass

    def reset(self):
        if super().reset():
            for operand in self.operands:
                operand.reset()


class And(Operator):
    def add_constraint(self, m, gap, logic):
        if self.logic is not None:
            logic = self.logic

        if logic is Logic.GODEL:
            m.add_constraint(self.val == m.min(operand.val for operand in self.operands))

        else:  # logic is Logic.LUKASIEWICZ
            m.add_constraint(self.val == m.max(0, 1 - m.sum(1 - operand.val for operand in self.operands)))


class WeakAnd(And):
    def __init__(self, *args):
        super().__init__(*args, logic=Logic.GODEL)


class Or(Operator):
    def add_constraint(self, m, gap, logic):
        if self.logic is not None:
            logic = self.logic

        if logic is Logic.GODEL:
            m.add_constraint(self.val == m.max(operand.val for operand in self.operands))

        else:  # logic is Logic.LUKASIEWICZ
            m.add_constraint(self.val == m.min(1, m.sum(operand.val for operand in self.operands)))


class WeakOr(Or):
    def __init__(self, *args):
        super().__init__(*args, logic=Logic.GODEL)


class Implies(Operator):
    def __init__(self, lhs, rhs, logic=None):
        super().__init__(lhs, rhs, logic=logic)

        self.lhs = self.operands[0]
        self.rhs = self.operands[1]

    def add_constraint(self, m, gap, logic):
        if self.logic is not None:
            logic = self.logic

        if logic is Logic.GODEL:
            lhs_le_rhs = m.binary_var(name=str(self) + ".lhs_le_rhs")

            m.add_indicator(lhs_le_rhs, self.lhs.val <= self.rhs.val)
            m.add_indicator(lhs_le_rhs, self.val == 1)

            m.add_indicator(lhs_le_rhs, self.lhs.val >= self.rhs.val + gap, 0)
            m.add_indicator(lhs_le_rhs, self.val == self.rhs.val, 0)

        else:  # logic is Logic.LUKASIEWICZ
            if isinstance(self.rhs.val, Number) and self.rhs.val == 0:
                m.add_constraint(self.val == 1 - self.lhs.val)
            else:
                m.add_constraint(self.val == m.min(1, 1 - self.lhs.val + self.rhs.val))


class Not(Implies):
    def __init__(self, arg, logic=None):
        super().__init__(arg, 0, logic=logic)


class Inv(Not):
    def __init__(self, arg):
        super().__init__(arg, logic=Logic.LUKASIEWICZ)


class Equiv(Operator):
    def __init__(self, lhs, rhs, logic=None):
        super().__init__(lhs, rhs, logic=logic)

        self.lhs = self.operands[0]
        self.rhs = self.operands[1]

    def add_constraint(self, m, gap, logic):
        if self.logic is not None:
            logic = self.logic

        if logic is Logic.GODEL:
            lhs_eq_rhs = m.binary_var(name=str(self) + ".lhs_eq_rhs")

            m.add_indicator(lhs_eq_rhs, self.lhs.val == self.rhs.val)
            m.add_indicator(lhs_eq_rhs, self.val == 1)

            m.add_indicator(lhs_eq_rhs, m.abs(self.lhs.val - self.rhs.val) >= gap, 0)
            m.add_indicator(lhs_eq_rhs, self.val == m.min(self.lhs.val, self.rhs.val), 0)

        else:  # logic is Logic.LUKASIEWICZ
            m.add_constraint(self.val == 1 - m.abs(self.lhs.val - self.rhs.val))


class Delta(Operator):
    def __init__(self, arg):
        super().__init__(arg)

        self.arg = self.operands[0]

    def add_constraint(self, m, gap, logic):
        arg_eq_one = m.binary_var(name=str(self) + ".arg_eq_one")

        m.add_indicator(arg_eq_one, self.arg.val == 1)
        m.add_indicator(arg_eq_one, self.val == 1)

        m.add_indicator(arg_eq_one, self.arg.val <= 1 - gap, 0)
        m.add_indicator(arg_eq_one, self.val == 0, 0)
