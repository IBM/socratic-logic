from socratic.clock import *
from socratic.op import *
from socratic.theory import *

MAX_SIZE = 5


def index(p):
    return int(p.name[1:])


def degree(f):
    if isinstance(f, Prop):
        return index(f) + 1

    if isinstance(f, Operator):
        return max(map(degree, f.operands))

    return 0


class TruthReq(Enum):
    AT_MOST = -1
    EQUAL = 0
    AT_LEAST = 1

    @property
    def neg(self):
        return TruthReq(-self.value)


def neg(f):
    return f.arg if isinstance(f, Not) else Not(f)


def specializes(f, a, req=TruthReq.EQUAL, mappings=None):
    if mappings is None:
        mappings = [[None] * degree(a)]

    ret_mappings = []

    if req is TruthReq.AT_LEAST and isinstance(f, Implies):
        ret_mappings += specializes(f.rhs, a, req, mappings)
        ret_mappings += specializes(neg(f.lhs), a, req, mappings)

    if req is TruthReq.AT_MOST and isinstance(f, Not) and isinstance(f.arg, Implies):
        ret_mappings += specializes(f.arg.lhs, a, req, mappings)
        ret_mappings += specializes(neg(f.arg.rhs), a, req, mappings)

    if isinstance(a, Prop):
        i = index(a)
        for mapping in mappings:
            if mapping[i] is None or mapping[i] == f:
                ret_mappings.append(list(mapping))
                ret_mappings[-1][i] = f

    elif isinstance(a, Not):
        ret_mappings += specializes(neg(f), a.arg, req.neg, mappings)

    elif isinstance(a, Implies) and isinstance(f, Implies):
        lhs_mappings = specializes(f.lhs, a.lhs, req.neg, mappings)
        ret_mappings += specializes(f.rhs, a.rhs, req, lhs_mappings)

        rhs_mappings = specializes(neg(f.rhs), a.lhs, req.neg, mappings)
        ret_mappings += specializes(neg(f.lhs), a.rhs, req, rhs_mappings)

    elif a == f:
        ret_mappings += mappings

    return ret_mappings


def all_formulae(size, n_symb_so_far=0):
    if size == 0:
        yield Prop(f'p{n_symb_so_far}'), n_symb_so_far + 1
        for idx in range(n_symb_so_far - 1, -1, -1):
            yield Prop(f'p{idx}'), n_symb_so_far

    for part in range(size):
        for lhs, lhs_degree in all_formulae(part, n_symb_so_far):
            for rhs, rhs_degree in all_formulae(size - part - 1, lhs_degree):
                if lhs != rhs:
                    yield Implies(lhs, rhs), rhs_degree

                    # if not isinstance(lhs, Prop) or lhs_degree == n_symb_so_far:
                    #     if not isinstance(rhs, Prop) or rhs_degree == lhs_degree:
                    #         yield Implies(Not(lhs), Not(rhs)), rhs_degree

                if 2 * part <= size - 1:
                    if not isinstance(rhs, Prop) or rhs_degree == lhs_degree:
                        yield Implies(lhs, Not(rhs)), rhs_degree

                if 2 * part >= size - 1:
                    if not isinstance(lhs, Prop) or lhs_degree == n_symb_so_far:
                        yield Implies(Not(lhs), rhs), rhs_degree


def all_axioms():
    empty_theory = Theory()

    axioms = []

    def check_if_axiom(f):
        for a in axioms:
            if specializes(f, a, TruthReq.AT_LEAST):
                print("      %-43s  specializes  %s" % (f, a))
                return

        if empty_theory.entails(f):
            axioms.append(f)
            print("%4d." % len(axioms), f)

    check_if_axiom(Implies('p0', 'p0'))

    for size in range(1, MAX_SIZE):
        for formula, _ in all_formulae(size):
            check_if_axiom(formula)


if __name__ == "__main__":
    clock(all_axioms)
