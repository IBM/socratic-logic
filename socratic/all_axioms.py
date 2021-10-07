from itertools import permutations, combinations

from socratic.clock import *
from socratic.op import *
from socratic.theory import *

MAX_SIZE = 4


def index(p):
    return int(p.name[1:])


def degree(f):
    if isinstance(f, Prop):
        return index(f) + 1

    if isinstance(f, Operator):
        return max(map(degree, f.operands))

    return 0


def all_perms(size, n_symb_so_far):
    perm = [-1] * size
    for k in range(min(size, n_symb_so_far) + 1):
        for selection in permutations(range(n_symb_so_far), k):
            for merger in combinations(range(size), size - k):
                prev = 0
                for i in range(size - k):
                    curr = merger[i]
                    perm[prev:curr] = selection[(prev - i):(curr - i)]
                    perm[curr] = n_symb_so_far + i
                    prev = curr + 1
                perm[prev:] = selection[(prev - size + k):]
                yield perm


def apply_perm(f, perm):
    if isinstance(f, Prop):
        return Prop(f"p{perm[index(f)]}")

    if isinstance(f, Operator):
        return type(f)(*(apply_perm(op, perm) for op in f.operands))

    return f


def specializes(f, a, mapping=None):
    if mapping is None:
        mapping = [None] * degree(a)

    if isinstance(a, Prop):
        i = index(a)
        if mapping[i] is None:
            mapping[i] = f
            return True
        return mapping[i] == f

    if isinstance(a, Operator):
        return (type(a) is type(f) and
                a.logic is f.logic and
                len(a.operands) == len(f.operands) and
                all(specializes(ff, aa, mapping) for aa, ff in zip(a.operands, f.operands)))

    return a == f


def all_axioms():
    empty_theory = Theory()

    formulae = [[Prop("p0")]]
    axioms = []

    def check_if_axiom(f):
        if not any(specializes(f, a) for a in axioms):
            if empty_theory.entails(f):
                axioms.append(f)
                print("%4d." % len(axioms), f)
            else:
                formulae[-1].append(f)

    for size in range(1, MAX_SIZE):
        formulae.append([])
        for part in range(size):
            for i in range(len(formulae[part])):
                lhs = formulae[part][i]
                lhs_degree = degree(lhs)
                for j in range(len(formulae[size - part - 1])):
                    rhs = formulae[size - part - 1][j]
                    rhs_degree = degree(rhs)
                    for perm in all_perms(rhs_degree, lhs_degree):
                        perm_rhs = apply_perm(rhs, perm)

                        check_if_axiom(Implies(lhs, perm_rhs))

                        if 2 * part < size - 1 or 2 * part == size - 1 and i <= j:
                            check_if_axiom(Implies(Not(lhs), perm_rhs))

                        if 2 * part > size - 1 or 2 * part == size - 1 and i >= j:
                            check_if_axiom(Implies(lhs, Not(perm_rhs)))


if __name__ == "__main__":
    clock(all_axioms)
