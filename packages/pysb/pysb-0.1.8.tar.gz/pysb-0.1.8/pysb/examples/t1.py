from pysb import *

Model()

Monomer('a', ['s'])
Monomer('b', ['s'])
Parameter('p', 1)
Parameter('q', 2)
Initial(a(s=1) % b(s=1),p)
Initial(b(s=1) % a(s=1),q)
Observable('b', b())


if __name__ == '__main__':
    from pysb.integrate import odesolve
    t = range(0, 10)
    y = odesolve(model, t)
    print y.dtype
    print y
