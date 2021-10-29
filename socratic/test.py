import itertools
import random
import unittest

from socratic.clock import *
from socratic.op import *
from socratic.theory import *


class SatTestCase(unittest.TestCase):
    def sat_test(self, k):
        x = [Prop("x_%d" % k) for k in range(k)]

        s = [Or(*c) for c in itertools.product(*([a, Inv(a)] for a in x))]
        full_theory = Theory(*s)

        # The problem is unsatisfiable in Godel (and classical) logic
        try:
            self.assertFalse(clock(full_theory.satisfiable, logic=Logic.GODEL))
        except AssertionError:
            print()
            print("k=%d" % k)
            full_theory.m.print_solution(print_zeros=True)
            print()
            raise

        # Removing any one sentence renders it satisfiable
        i = random.randrange(len(s))
        partial_theory = Theory(*(s[:i] + s[i+1:]))
        self.assertTrue(clock(partial_theory.satisfiable, logic=Logic.GODEL))

        # The problem is likewise satisfiable in Lukasiewicz logic
        self.assertTrue(clock(full_theory.satisfiable, logic=Logic.LUKASIEWICZ))

        exclusions = [SimpleSentence(a, [LessThan(1/k), GreaterThan((k-1)/k)]) for a in x]
        excluded_theory = Theory(*(s + exclusions))

        # The problem becomes unsatisfiable again if propositions are forced to lie near 0 and 1
        try:
            self.assertFalse(clock(excluded_theory.satisfiable, logic=Logic.LUKASIEWICZ))
        except AssertionError:
            print()
            print("k=%d" % k)
            excluded_theory.m.print_solution(print_zeros=True)
            print()
            raise

        # Removing any one sentence again renders it satisfiable
        i = random.randrange(len(s))
        partial_excluded_theory = Theory(*(s[:i] + s[i+1:] + exclusions))
        self.assertTrue(clock(partial_excluded_theory.satisfiable, logic=Logic.LUKASIEWICZ))

    def test_sat(self):
        for k in range(3, 7):
            with self.subTest(k=k):
                clock(self.sat_test, k)
                print()


class HajekTestCase(unittest.TestCase):
    def hajek_test(self, formulae, logics=Logic):
        empty_theory = Theory()

        for logic in logics:
            for formula in formulae:
                with self.subTest(formula=str(formula), logic=str(logic)):
                    try:
                        self.assertTrue(empty_theory.entails(formula, logic=logic))
                    except AssertionError:
                        print()
                        print(str(formula), str(logic))
                        empty_theory.m.print_solution(print_zeros=True)
                        print()
                        raise

    def hajek_test_false(self, formulae, logics=Logic):
        empty_theory = Theory()

        for logic in logics:
            for formula in formulae:
                with self.subTest(formula=str(formula), logic=str(logic)):
                    self.assertFalse(empty_theory.entails(formula, logic=logic))

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

    def test_hajek_lukasiewicz(self):
        from socratic.hajek import lukasiewicz
        clock(self.hajek_test, lukasiewicz, logics=[Logic.LUKASIEWICZ])
        clock(self.hajek_test_false, lukasiewicz, logics=[Logic.GODEL])

    def test_hajek_godel(self):
        from socratic.hajek import godel
        clock(self.hajek_test, godel, logics=[Logic.GODEL])
        clock(self.hajek_test_false, godel, logics=[Logic.LUKASIEWICZ])


class BooleanTestCase(unittest.TestCase):
    def boolean_test(self, logic):
        phi = Prop("phi")
        psi = Prop("psi")

        formula = Implies(Implies(phi, psi), Implies(Implies(Not(phi), psi), psi))

        empty_theory = Theory()

        self.assertFalse(empty_theory.entails(formula, logic=logic))

        boolean_theory = Theory(
            SimpleSentence(phi, [0, 1]),
            SimpleSentence(psi, [0, 1]),
        )

        self.assertTrue(boolean_theory.entails(formula, logic=logic))

    def test_boolean_godel(self):
        clock(self.boolean_test, Logic.GODEL)

    def test_boolean_lukasiewicz(self):
        clock(self.boolean_test, Logic.LUKASIEWICZ)


class StressTestCase(unittest.TestCase):
    def stress_test(self, logic):
        phi = Prop("phi")
        psi = Prop("psi")

        formula = Implies(Implies(phi, psi), Implies(Implies(Not(phi), psi), psi))

        s = SimpleSentence(formula, [ClosedInterval(1/(k + 1), 1/k) for k in range(2, 10000)] + [AtLeast(.5)])

        boolean_theory = Theory(
            SimpleSentence(phi, [0] + [ClosedInterval(1 - 1/k, 1 - 1/(k + 1)) for k in range(2, 10000)]),
            SimpleSentence(psi, [0] + [ClosedInterval(1 - 1/k, 1 - 1/(k + 1)) for k in range(2, 10000)]),
        )

        self.assertTrue(boolean_theory.entails(s, logic=logic))

    def test_stress_godel(self):
        clock(self.stress_test, Logic.GODEL)

    def test_stress_lukasiewicz(self):
        clock(self.stress_test, Logic.LUKASIEWICZ)


if __name__ == '__main__':
    unittest.main()
