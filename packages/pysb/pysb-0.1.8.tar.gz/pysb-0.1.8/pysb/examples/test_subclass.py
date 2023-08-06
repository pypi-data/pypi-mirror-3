from pysb import *

class Nucleotide(Monomer):
    def __init__(self, *args, **kwargs):
        Monomer.__init__(self, *args, **kwargs)
        self.sites += ['r5p', 'r3p']

class RNA(Nucleotide):
    pass

Model()

RNA('mRNA_1')
RNA('mRNA_2')
Nucleotide('A')
Monomer('NULL')
Parameter('k1', 4.0e-3)

for M in model.monomers:
    if isinstance(M, RNA):
        Rule('%s_deg' % M.name, M(r3p=None) >> NULL(), k1)
