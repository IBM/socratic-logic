from socratic.clock import *
from socratic.op import *
from socratic.theory import *

MAX_SIZE = 4


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

                    if empty_theory.entails(SimpleSentence(f, 1)):
                        print(f)


if __name__ == "__main__":
    clock(all_axioms)
