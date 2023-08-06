from pysb import *

Model()

Monomer('E', ['s'])
Monomer('S', ['e', 'act', 'other', 'b2'], {'act': ['y', 'n'], 'other': ['x','y']})
Monomer('P', ['other'])

Parameter('k', 1)

Rule('bind', E(s=None) + S(e=None, act='n') <> E(s=1) % S(e=1, act='n'), k, k)
Rule('prod', E(s=1) % S(e=1, act='n') >> E(s=None) + S(e=None, act='y'), k)

#Rule('bind2', E(s=None) + S(e=None, act='n') <> E(s=1) % S(e=1, act='n'), k, k)
#Rule('prod2', E(s=1) % S(e=1, act='n') >> E(s=None) + P(other=None), k)

Initial(E(s=None), k)
Initial(S(e=None, act='n', other='x', b2=None), k)
Initial(S(e=None, act='n', other='y', b2=None), k)
