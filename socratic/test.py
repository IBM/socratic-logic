import itertools
import unittest

from socratic.clock import *
from socratic.op import *
from socratic.theory import *


class SatTestCase(unittest.TestCase):
    def sat_test(self, k):
        x = [Prop(k) for k in range(k)]

        s = [SimpleSentence(Or(c), 1) for c in itertools.product(*([a, Not(a)] for a in x))]

        theories = [Theory(s[:i] + s[i+1:]) for i in range(len(s))]

        # The problem is unsatisfiable in Godel (and classical) logic
        self.assertFalse(clock(Theory(s).satisfiable, logic=Logic.GODEL))

        # Removing any one sentence renders it satisfiable
        for theory in theories:
            self.assertTrue(theory.satisfiable(logic=Logic.GODEL))

        # The problem is likewise satisfiable in Lukasiewicz logic
        self.assertTrue(clock(Theory(s).satisfiable, logic=Logic.LUKASIEWICZ))

    def test_sat(self):
        for i in [3, 4, 5, 6]:
            with self.subTest(i=i):
                clock(self.sat_test, i)
                print()


if __name__ == '__main__':
    unittest.main()
