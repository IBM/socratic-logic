import unittest

from socratic.clock import *
from socratic.op import *
from socratic.theory import *


class SatTestCase(unittest.TestCase):
    def test_sat(self):
        x = Prop("x")
        y = Prop("y")
        z = Prop("z")

        s = [
            SimpleSentence(Or(x, y, z), 1),
            SimpleSentence(Or(x, y, Not(z)), 1),
            SimpleSentence(Or(x, Not(y), z), 1),
            SimpleSentence(Or(Not(x), y, z), 1),
            SimpleSentence(Or(x, Not(y), Not(z)), 1),
            SimpleSentence(Or(Not(x), y, Not(z)), 1),
            SimpleSentence(Or(Not(x), Not(y), z), 1),
            SimpleSentence(Or(Not(x), Not(y), Not(z)), 1)
        ]

        theories = [Theory(s[:i] + s[i+1:]) for i in range(len(s))]

        # The problem is unsatisfiable in Godel (and classical) logic
        self.assertFalse(clock(Theory(s).satisfiable, logic=Logic.GODEL))

        # Removing any one sentence renders it satisfiable
        for theory in theories:
            self.assertTrue(theory.satisfiable(logic=Logic.GODEL))

        # The problem is likewise satisfiable in Lukasiewicz logic
        self.assertTrue(clock(Theory(s).satisfiable, logic=Logic.LUKASIEWICZ))


if __name__ == '__main__':
    unittest.main()
