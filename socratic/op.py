class Formula(object):
    def __init__(self):
        self.val = None

    def configure(self, m):
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


class Operator(Formula):
    def __init__(self, *args):
        super().__init__()

        self.operands = args

    def configure(self, m):
        if super().configure(m):
            for operand in self.operands:
                operand.configure(m)

            self.add_constraint(m)

    def add_constraint(self, m):
        pass

    def reset(self):
        if super().reset():
            for operand in self.operands:
                operand.reset()


class And(Operator):
    def add_constraint(self, m):
        m.add_constraint(self.val == m.max(0, m.sum_vars(operand.val for operand in self.operands) - len(self.operands) + 1))


class Or(Operator):
    def add_constraint(self, m):
        m.add_constraint(self.val == m.min(1, m.sum_vars(operand.val for operand in self.operands)))


class Not(Operator):
    def __init__(self, arg):
        super().__init__(arg)

        self.arg = arg

    def add_constraint(self, m):
        m.add_constraint(self.val == 1 - self.arg.val)


class Implies(Operator):
    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs)

        self.lhs = lhs
        self.rhs = rhs

    def add_constraint(self, m):
        m.add_constraint(self.val == m.min(1, 1 - self.lhs.val + self.rhs.val))
