from socratic.op import *


phi = Prop('phi')
psi = Prop('psi')
chi = Prop('chi')
omega = Prop('omega')

axioms = [
    Implies(Implies(phi, psi), Implies(Implies(psi, chi), Implies(phi, chi))),
    Implies(And(phi, psi), phi),
    Implies(And(phi, psi), And(psi, phi)),
    Implies(And(phi, Implies(phi, psi)), And(psi, Implies(psi, phi))),
    Implies(Implies(phi, Implies(psi, chi)), Implies(And(phi, psi), chi)),
    Implies(Implies(And(phi, psi), chi), Implies(phi, Implies(psi, chi))),
    Implies(Implies(Implies(phi, psi), chi), Implies(Implies(Implies(psi, phi), chi), chi)),
    Implies(0, phi),
]

implication = [
    Implies(phi, Implies(psi, phi)),
    Implies(Implies(phi, Implies(psi, chi)), Implies(psi, Implies(phi, chi))),
    Implies(phi, phi),
]

conjunction = [
    Implies(And(phi, Implies(phi, psi)), psi),
    Implies(phi, Implies(psi, And(phi, psi))),
    Implies(Implies(phi, psi), Implies(And(phi, chi), And(psi, chi))),
    Implies(And(Implies(phi, psi), Implies(chi, omega)), Implies(And(phi, chi), And(psi, omega))),
    Implies(And(And(phi, psi), chi), And(phi, And(psi, chi))),
    Implies(And(phi, And(psi, chi)), And(And(phi, psi), chi)),
]

weak_conjunction = [
    Implies(WeakAnd(phi, psi), phi),
    Implies(WeakAnd(phi, psi), psi),
    Implies(And(phi, psi), WeakAnd(phi, psi)),
    Implies(Implies(phi, psi), Implies(phi, WeakAnd(phi, psi))),
    Implies(WeakAnd(phi, psi), WeakAnd(psi, phi)),
    Implies(WeakAnd(Implies(phi, psi), Implies(phi, chi)), Implies(phi, WeakAnd(psi, chi))),
    Implies(And(Implies(phi, psi), Implies(phi, chi)), Implies(phi, WeakAnd(psi, chi))),
]

weak_disjunction = [
    Implies(phi, WeakOr(phi, psi)),
    Implies(psi, WeakOr(phi, psi)),
    Implies(WeakOr(phi, psi), WeakOr(psi, phi)),
    Implies(Implies(phi, psi), Implies(WeakOr(phi, psi), psi)),
    WeakOr(Implies(phi, psi), Implies(psi, phi)),
    Implies(WeakAnd(Implies(phi, chi), Implies(psi, chi)), Implies(WeakOr(phi, psi), chi)),
    Implies(And(Implies(phi, chi), Implies(psi, chi)), Implies(WeakOr(phi, psi), chi)),
]

negation = [
    Implies(phi, Implies(Not(phi), psi)),
    Implies(phi, Not(Not(phi))),
    Implies(And(phi, Not(phi)), 0),
    Implies(Implies(phi, And(psi, Not(psi))), Not(phi)),
    Implies(Implies(phi, psi), Implies(Not(psi), Not(phi))),
    Implies(Implies(phi, Not(psi)), Implies(psi, Not(phi))),
    # Implies(0, 0),
    Implies(phi, And(1, phi)),
    Implies(Implies(1, phi), phi),
]

associativity = [
    Implies(WeakAnd(phi, WeakAnd(psi, chi)), WeakAnd(WeakAnd(phi, psi), chi)),
    Implies(WeakAnd(WeakAnd(phi, psi), chi), WeakAnd(phi, WeakAnd(psi, chi))),
    Implies(WeakOr(phi, WeakOr(psi, chi)), WeakOr(WeakOr(phi, psi), chi)),
    Implies(WeakOr(WeakOr(phi, psi), chi), WeakOr(phi, WeakOr(psi, chi))),
    Implies(phi, WeakAnd(phi, WeakOr(phi, psi))),
    Implies(WeakOr(phi, WeakAnd(phi, psi)), phi),
]

equivalence = [
    Equiv(phi, phi),
    Implies(Equiv(phi, psi), Equiv(psi, phi)),
    Implies(And(Equiv(phi, psi), Equiv(psi, chi)), Equiv(phi, chi)),
    Implies(Equiv(phi, psi), Implies(phi, psi)),
    Implies(Equiv(phi, psi), Implies(psi, phi)),
    Implies(Equiv(phi, psi), Equiv(And(phi, chi), And(psi, chi))),
    Implies(Equiv(phi, psi), Equiv(Implies(phi, chi), Implies(psi, chi))),
    Implies(Equiv(phi, psi), Equiv(Implies(chi, phi), Implies(chi, psi))),
    Implies(Equiv(phi, psi), WeakAnd(Implies(phi, psi), Implies(psi, phi))),
]

distributivity = [
    Equiv(And(phi, WeakOr(psi, chi)), WeakOr(And(phi, psi), And(phi, chi))),
    Equiv(And(phi, WeakAnd(psi, chi)), WeakAnd(And(phi, psi), And(phi, chi))),
    Equiv(WeakAnd(phi, WeakOr(psi, chi)), WeakOr(WeakAnd(phi, psi), WeakAnd(phi, chi))),
    Equiv(WeakOr(phi, WeakAnd(psi, chi)), WeakAnd(WeakOr(phi, psi), WeakOr(phi, chi))),
    Implies(And(WeakOr(phi, psi), WeakOr(phi, psi)), WeakOr(And(phi, phi), And(psi, psi))),
    Implies(And(WeakAnd(phi, psi), WeakAnd(phi, psi)), WeakAnd(And(phi, phi), And(psi, psi))),
    # WeakOr(And(Implies(phi, psi) ** n), And(Implies(psi, phi) ** n)),
    Equiv(WeakAnd(Not(phi), Not(psi)), Not(WeakOr(phi, psi))),
    Equiv(WeakOr(Not(phi), Not(psi)), Not(WeakAnd(phi, psi))),
]

delta_operator = [
    Equiv(Delta(phi), Delta(And(phi, phi))),
    Equiv(Delta(phi), And(Delta(phi), Delta(phi))),
    # Implies(Delta(phi), phi ** n),
    Equiv(Delta(And(phi, psi)), And(Delta(phi), Delta(psi))),
]

lukasiewicz = [
    Equiv(Not(Not(phi)), phi),
    Equiv(Implies(phi, psi), Implies(Not(psi), Not(phi))),
    Equiv(Implies(phi, psi), Not(And(phi, Not(psi)))),
    Implies(Implies(Implies(phi, psi), psi), Implies(Implies(psi, phi), phi)),
    Equiv(Implies(Implies(phi, psi), psi), WeakOr(phi, psi)),
    Equiv(Not(WeakAnd(Not(phi), Not(psi))), WeakOr(phi, psi)),
    Equiv(Not(WeakOr(Not(phi), Not(psi))), WeakAnd(phi, psi)),
    Equiv(Not(And(Not(phi), Not(psi))), Or(phi, psi)),
    Equiv(Not(Or(Not(phi), Not(psi))), And(phi, psi)),
    # Equiv(WeakAnd(phi, psi), And(Or(phi, Not(psi)), psi)),
    Equiv(WeakOr(phi, psi), Or(And(phi, Not(psi)), psi)),
    Or(phi, Not(phi)),
    Equiv(Or(And(phi, Not(psi)), psi), Or(phi, And(psi, Not(phi)))),
    # Equiv(And(Or(phi, Not(psi)), psi), And(phi, Or(psi, Not(phi)))),
    # Implies(Implies(phi, chi), Implies(Implies(psi, chi), Implies(WeakOr(phi, psi), chi))),
]

godel = [
    Implies(phi, And(phi, phi)),
    Equiv(And(phi, psi), WeakAnd(phi, psi)),
    Equiv(And(phi, psi), And(phi, Implies(phi, psi))),
    Implies(Implies(phi, Implies(psi, chi)), Implies(Implies(phi, psi), Implies(phi, chi))),
    Implies(Implies(phi, Not(phi)), Not(phi)),
]
