class Formula(object):
    pass


class Prop(Formula):
    def __init__(self, name):
        pass


class Operator(Formula):
    pass


class And(Operator):
    def __init__(self, *args):
        pass


class Or(Operator):
    def __init__(self, *args):
        pass


class Not(Operator):
    def __init__(self, arg):
        pass


class Implies(Operator):
    def __init__(self, lhs, rhs):
        pass
