from enum import Enum
from numbers import Number


class Logic(Enum):
    GODEL = 0
    LUKASIEWICZ = 1


class Formula(object):
    def __init__(self):
        self.val = None

    def configure(self, m, gap, logic):
        if self.val is None:
            self.val = m.continuous_var(lb=0, ub=1)

            return True

    def reset(self):
        if self.val is not None:
            self.val = None

            return True


class Prop(Formula):
    def __init__(self, name):
        super().__init__()

        self.name = name


class Constant(Formula):
    def __init__(self, val):
        super().__init__()

        self.val = val

    def configure(self, m, gap, logic):
        pass

    def reset(self):
        pass


class Operator(Formula):
    def __init__(self, *args):
        super().__init__()

        self.operands = [Constant(arg) if isinstance(arg, Number) else arg for arg in args]

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
        if logic is Logic.GODEL:
            m.add_constraint(self.val == m.min(operand.val for operand in self.operands))

        else:  # logic is Logic.LUKASIEWICZ
            m.add_constraint(self.val == m.max(0, m.sum(operand.val for operand in self.operands) - len(self.operands) + 1))


class GodelAnd(And):
    def add_constraint(self, m, gap, logic):
        super().add_constraint(m, gap, Logic.GODEL)


class LukasiewiczAnd(And):
    def add_constraint(self, m, gap, logic):
        super().add_constraint(m, gap, Logic.LUKASIEWICZ)


class Or(Operator):
    def add_constraint(self, m, gap, logic):
        if logic is Logic.GODEL:
            m.add_constraint(self.val == m.max(operand.val for operand in self.operands))

        else:  # logic is Logic.LUKASIEWICZ
            m.add_constraint(self.val == m.min(1, m.sum(operand.val for operand in self.operands)))


class GodelOr(Or):
    def add_constraint(self, m, gap, logic):
        super().add_constraint(m, gap, Logic.GODEL)


class LukasiewiczOr(Or):
    def add_constraint(self, m, gap, logic):
        super().add_constraint(m, gap, Logic.LUKASIEWICZ)


class Not(Operator):
    def __init__(self, arg):
        super().__init__(arg)

        self.arg = self.operands[0]

    def add_constraint(self, m, gap, logic):
        m.add_constraint(self.val == 1 - self.arg.val)


class Implies(Operator):
    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs)

        self.lhs = self.operands[0]
        self.rhs = self.operands[1]

    def add_constraint(self, m, gap, logic):
        if logic is Logic.GODEL:
            lhs_le_rhs = m.binary_var()

            m.add_indicator(lhs_le_rhs, self.lhs.val <= self.rhs.val)
            m.add_indicator(lhs_le_rhs, self.val == 1)

            m.add_indicator(lhs_le_rhs, self.lhs.val >= self.rhs.val + gap, 0)
            m.add_indicator(lhs_le_rhs, self.val == self.rhs.val, 0)

        else:  # logic is Logic.LUKASIEWICZ
            m.add_constraint(self.val == m.min(1, 1 - self.lhs.val + self.rhs.val))


class GodelImplies(Implies):
    def add_constraint(self, m, gap, logic):
        super().add_constraint(m, gap, Logic.GODEL)


class LukasiewiczImplies(Implies):
    def add_constraint(self, m, gap, logic):
        super().add_constraint(m, gap, Logic.LUKASIEWICZ)
