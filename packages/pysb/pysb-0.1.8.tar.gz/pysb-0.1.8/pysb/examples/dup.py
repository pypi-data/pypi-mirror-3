from pysb import *

Model()

x=1
Parameter('x')

Monomer('x')  # FIXME should be an error!

Parameter('y')
Parameter('y')


