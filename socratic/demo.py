from socratic.op import *
from socratic.theory import *

if __name__ == "__main__":
    whiskers = Prop("whiskers")
    tail = Prop("tail")
    cat = Prop("cat")
    dog = Prop("dog")
    pet = Prop("pet")

    theory = Theory(
        SimpleSentence(Implies(And(whiskers, tail), cat), [ClosedRange(.75, 1)]),
        SimpleSentence(Implies(Or(cat, dog), pet), [ClosedRange(.75, 1)])
    )

    query = SimpleSentence(Implies(Not(pet), Not(tail)), [ClosedRange(.5, 1)])

    import time

    t = time.time()

    res = theory.entails(query)

    t = time.time() - t

    print("res: ", res)
    print()
    print("time: ", t)
