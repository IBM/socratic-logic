from socratic.op import *
from socratic.theory import *

if __name__ == "__main__":
    whiskers = Prop("whiskers")
    tail = Prop("tail")
    cat = Prop("cat")
    dog = Prop("dog")
    pet = Prop("pet")

    s1 = SimpleSentence(Implies(And(whiskers, tail), cat), [ClosedRange(.75, 1)])
    s2 = SimpleSentence(Implies(Or(cat, dog), pet), [ClosedRange(.75, 1)])
    s3 = SimpleSentence(Not(And(cat, dog)), [ClosedRange(1, 1)])

    theory1 = Theory(s1, s2)
    theory2 = Theory(s1, s2, s3)

    goal = Not(tail)

    query1 = SimpleSentence(Implies(And(whiskers, Not(pet)), goal), [ClosedRange(.5, 1)])
    query2 = SimpleSentence(Implies(And(whiskers, dog), goal), [ClosedRange(.5, 1)])

    import time

    t = time.time()

    print("theory1, query1: ", theory1.entails(query1))
    print("theory1, query2: ", theory1.entails(query2))
    print("theory2, query1: ", theory2.entails(query1))
    print("theory2, query2: ", theory2.entails(query2))

    t = time.time() - t

    print()
    print("time: ", t)
