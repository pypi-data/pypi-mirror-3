from pysb import *
import pysb.macros

Model()

Monomer('Bax', ['s1', 's2', 'b'])
Monomer('Smac', ['b', 'loc'], {'loc': ['M', 'C']})

size = 4
pysb.macros.assemble_pore_sequential(Bax, 's1', 's2', size,
                                     [[1e-6, 1e-3]] * (size - 1))

max_size = 4
min_size = 3
pysb.macros.pore_transport(Bax, 's1', 's2', 'b', min_size, max_size,
                           Smac(loc='M'), 'b', Smac(loc='C'),
                           [[1e-7, 1e-3, 1e1]] * (max_size - min_size + 1))

Parameter('Bax_0', 1e5)
Initial(Bax(s1=None, s2=None, b=None), Bax_0)

Parameter('Smac_0', 1e2)
Initial(Smac(b=None, loc='M'), Smac_0)
