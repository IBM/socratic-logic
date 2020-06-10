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


class HajekTestCase(unittest.TestCase):
    def hajek_test(self, formulae):
        empty_theory = Theory()

        for logic in Logic:
            for formula in formulae:
                with self.subTest(formula=str(formula), logic=str(logic)):
                    self.assertTrue(empty_theory.entails(SimpleSentence(formula, 1), logic=logic))

    def test_hajek_axioms(self):
        from socratic.hajek import axioms
        clock(self.hajek_test, axioms)

    def test_hajek_implication(self):
        from socratic.hajek import implication
        clock(self.hajek_test, implication)

    def test_hajek_conjunction(self):
        from socratic.hajek import conjunction
        clock(self.hajek_test, conjunction)

    def test_hajek_weak_conjunction(self):
        from socratic.hajek import weak_conjunction
        clock(self.hajek_test, weak_conjunction)

    def test_hajek_weak_disjunction(self):
        from socratic.hajek import weak_disjunction
        clock(self.hajek_test, weak_disjunction)

    def test_hajek_negation(self):
        from socratic.hajek import negation
        clock(self.hajek_test, negation)

    def test_hajek_associativity(self):
        from socratic.hajek import associativity
        clock(self.hajek_test, associativity)

    def test_hajek_equivalence(self):
        from socratic.hajek import equivalence
        clock(self.hajek_test, equivalence)

    def test_hajek_distributivity(self):
        from socratic.hajek import distributivity
        clock(self.hajek_test, distributivity)

    def test_hajek_delta_operator(self):
        from socratic.hajek import delta_operator
        clock(self.hajek_test, delta_operator)


if __name__ == '__main__':
    unittest.main()
