from pysb import *

# A test of applying multiple bonds to the same site

Model()

# These are all dummy values, since we are really just interested in the rule application and
# resultant species, not simulation.
Parameter('Bak_0', 10)
Parameter('Mcl1_0', 20)
Parameter('tet_0', 30)
Parameter('kbak2f', 1)
Parameter('kbak2r', 1)
Parameter('kbak4f', 1)
Parameter('kbak4r', 1)
Parameter('kinhf', 1)
Parameter('kinhr', 1)

Monomer('Bak', ['b'])
Monomer('Mcl1', ['b'])

Rule('Bak_dimerize',
     Bak(b=None) + Bak(b=None) <> Bak(b=1) % Bak(b=1),
     kbak2f, kbak2r)

Rule('Bak_tetramerize',
     Bak(b=1) % Bak(b=1) + Bak(b=1) % Bak(b=1) <> Bak(b=[1,2]) % Bak(b=[2,3]) % Bak(b=[3,4]) % Bak(b=[4,1]),
     kbak4f, kbak4f)

# Mcl1 competetively binds the Bak dimerization site
Rule('Mcl1_inhibit_Bak',
     Bak(b=None) + Mcl1(b=None) <> Bak(b=1) % Mcl1(b=1),
     kinhf, kinhr)

Initial(Bak(b=None), Bak_0)
Initial(Mcl1(b=None), Mcl1_0)
Initial(Bak(b=[1,2]) % Bak(b=[2,3]) % Bak(b=[3,4]) % Bak(b=[4,1]), tet_0)
