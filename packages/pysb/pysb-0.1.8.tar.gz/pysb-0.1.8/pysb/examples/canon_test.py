from pysb import *

Model()

Monomer('Bak', ['b'])

Parameter('Bak_0', 1)
Parameter('tet_0', 1)
Parameter('kf', 1)

Rule('tetramerize',
     Bak(b=None) + Bak(b=None) + Bak(b=None) + Bak(b=None) >>
     Bak(b=[1,2]) % Bak(b=[2,3]) % Bak(b=[3,4]) % Bak(b=[4,1]),
     kf)

Initial(Bak(b=None), Bak_0)
Initial(Bak(b=[2,1]) % Bak(b=[2,3]) % Bak(b=[4,1]) % Bak(b=[3,4]), tet_0)
