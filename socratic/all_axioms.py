from socratic.clock import *
from socratic.op import *
from socratic.theory import *

MAX_SIZE = 4


def filter_props(f, max_so_far=0):
    if isinstance(f, Prop):
        next_name = f"p{max_so_far}"
        if f.name > next_name:
            return
        if f.name == next_name:
            max_so_far += 1

    if isinstance(f, Operator):
        for op in f.operands:
            max_so_far = filter_props(op, max_so_far)
            if max_so_far is None:
                return

    return max_so_far


def all_axioms():
    empty_theory = Theory()

    formulae = [[Prop(f"p{i}") for i in range(MAX_SIZE - 1)] + [0]]

    for size in range(1, MAX_SIZE):
        formulae.append([])
        for part in range(size):
            for lhs in formulae[part]:
                for rhs in formulae[size - part - 1]:
                    f = Implies(lhs, rhs)
                    formulae[-1].append(f)

                    if filter_props(f) and empty_theory.entails(SimpleSentence(f, 1)):
                        print(f)


if __name__ == "__main__":
    clock(all_axioms)
