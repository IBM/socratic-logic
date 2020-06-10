from socratic.clock import *
from socratic.op import *
from socratic.theory import *


def demo_cat():
    whiskers = Prop("whiskers")
    tail = Prop("tail")
    cat = Prop("cat")
    dog = Prop("dog")
    pet = Prop("pet")

    s1 = SimpleSentence(Implies(And(whiskers, tail), cat), [ClosedRange(.75, 1)])
    s2 = SimpleSentence(Implies(Or(cat, dog), pet, logic=Logic.GODEL), [ClosedRange(.75, 1)])
    s3 = SimpleSentence(Not(And(cat, dog)), ClosedRange(1, 1))  # Single range not given as list
    s4 = SimpleSentence(WeakAnd(cat, dog), 1)  # Atomic range given as Number

    theory1 = Theory(s1, s2)
    theory2 = Theory(s1, s2, s3)
    theory3 = Theory(s1, s2, s3, s4)

    goal = Not(tail)

    query1 = SimpleSentence(Implies(And(whiskers, Not(pet)), goal), [ClosedRange(.5, 1)])
    query2 = SimpleSentence(Implies(And(whiskers, dog), goal), [ClosedRange(.5, 1)])

    print("theory1 satisfiable: ", theory2.satisfiable())
    print("theory2 satisfiable: ", theory2.satisfiable())
    print("theory3 satisfiable: ", theory3.satisfiable())
    print("theory1, query1: ", theory1.entails(query1))
    print("theory1, query2: ", theory1.entails(query2))
    print("theory2, query1: ", theory2.entails(query1))
    print("theory2, query2: ", theory2.entails(query2))


def demo_3sat():
    x = Prop("x")
    y = Prop("y")
    z = Prop("z")

    val = 1

    s = [
        SimpleSentence(Or(x, y, z), val),
        SimpleSentence(Or(x, y, Not(z)), val),
        SimpleSentence(Or(x, Not(y), z), val),
        SimpleSentence(Or(Not(x), y, z), val),
        SimpleSentence(Or(x, Not(y), Not(z)), val),
        SimpleSentence(Or(Not(x), y, Not(z)), val),
        SimpleSentence(Or(Not(x), Not(y), z), val),
        SimpleSentence(Or(Not(x), Not(y), Not(z)), val)
    ]

    theories = [Theory(s[:i] + s[i+1:]) for i in range(len(s))]

    print("theory satisfiable: ", Theory(s).satisfiable(logic=Logic.GODEL))
    for theory in theories:
        print("theory satisfiable: ", theory.satisfiable(logic=Logic.GODEL))


if __name__ == "__main__":
    clock(demo_cat)
    clock(demo_3sat)
