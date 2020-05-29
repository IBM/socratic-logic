class Formula(object):
    def __init__(self):
        self.val = None

    def configure(self, m):
        if self.val is None:
            self.val = m.continuous_var(lb=0, ub=1)


class Prop(Formula):
    def __init__(self, name):
        super().__init__()

        self.name = name


class Operator(Formula):
    def __init__(self, *args):
        super().__init__()

        self.operands = args

    def configure(self, m):
        super().configure(m)

        for operand in self.operands:
            operand.configure(m)


class And(Operator):
    def __init__(self, *args):
        super().__init__(*args)

    def configure(self, m):
        super().configure(m)

        m.add_constraint(self.val == m.max(0, m.sum(operand.val for operand in self.operands) - len(self.operands) + 1))


class Or(Operator):
    def __init__(self, *args):
        super().__init__(*args)

    def configure(self, m):
        super().configure(m)

        m.add_constraint(self.val == m.min(1, m.sum(operand.val for operand in self.operands)))


class Not(Operator):
    def __init__(self, arg):
        super().__init__(arg)

        self.arg = arg

    def configure(self, m):
        super().configure(m)

        m.add_constraint(self.val == 1 - self.arg.val)


class Implies(Operator):
    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs)

        self.lhs = lhs
        self.rhs = rhs

    def configure(self, m):
        super().configure(m)

        m.add_constraint(self.val == m.min(1, 1 - self.lhs.val + self.rhs.val))
