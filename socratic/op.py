class Formula(object):
    def __init__(self):
        self.val = None

    def configure(self, m):
        if self.val is None:
            self.val = m.continuous_var()


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


class Or(Operator):
    def __init__(self, *args):
        super().__init__(*args)


class Not(Operator):
    def __init__(self, arg):
        super().__init__(arg)


class Implies(Operator):
    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs)

        self.lhs = lhs
        self.rhs = rhs
