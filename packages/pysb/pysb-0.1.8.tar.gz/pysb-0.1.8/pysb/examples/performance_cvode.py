import pysb.bng
import numpy
import distutils.errors
import sympy
import re
from scipy.weave import inline
from pysundials import cvode
import ctypes
from pylab import *

from robertson import model

t = linspace(0, 40)
integrator_name = 'cvode'
integrator_options = {}


#####

use_inline = False
# try to inline a C statement to see if inline is functional
try:
    inline('int i;', force=1)
    use_inline = True
except distutils.errors.CompileError as e:
    pass

# try to load our pysundials cvode wrapper for scipy.integrate.ode
try:
    import pysb.pysundials_helpers
except ImportError as e:
    print e
    pass

# some sane default options for a few well-known integrators
default_integrator_options = {
    'vode': {
        'method': 'bdf',
        'with_jacobian': True,
        },
    'cvode': {
        'method': 'bdf',
        'iteration': 'newton',
        },
    }

global rhs_count
pysb.bng.generate_equations(model)

param_subs = dict([ (p.name, p.value) for p in model.parameters ])
param_values = numpy.array([param_subs[p.name] for p in model.parameters])
param_indices = dict( (p.name, i) for i, p in enumerate(model.parameters) )

code_eqs = '\n'.join(['ydot[%d] = %s;' % (i, sympy.ccode(model.odes[i])) for i in range(len(model.odes))])
code_eqs = re.sub(r's(\d+)', lambda m: 'y[%s]' % (int(m.group(1))), code_eqs)
for i, p in enumerate(model.parameters):
    code_eqs = re.sub(r'\b(%s)\b' % p.name, 'p[%d]' % i, code_eqs)

# If we can't use weave.inline to run the C code, compile it as Python code instead for use with
# exec. Note: C code with array indexing, basic math operations, and pow() just happens to also
# be valid Python.  If the equations ever have more complex things in them, this might fail.
if not use_inline:
    code_eqs_py = compile(code_eqs, '<%s odes>' % model.name, 'exec')

y0 = numpy.zeros((len(model.odes),))
for cp, ic_param in model.initial_conditions:
    si = model.get_species_index(cp)
    y0[si] = ic_param.value

rhs_count = 0

def cvode_rhs_func(t, y, ydot, f_data):
    global rhs_count
    rhs_count+=1
    # note that the evaluated code sets ydot as a side effect
    y = y.asarray()
    ydot = ydot.asarray()
    p = ctypes.py_object.from_address(f_data).value
    if use_inline:
        inline(code_eqs, ['ydot', 't', 'y', 'p']);
    else:
        exec code_eqs_py in locals()
    return 0

nspecies = len(model.species)
obs_names = [name for name, rp in model.observable_patterns]
rec_names = ['__s%d' % i for i in range(nspecies)] + obs_names
yout = numpy.ndarray((len(t), len(rec_names)))

y = cvode.NVector(y0)
cvode_mem = cvode.CVodeCreate(cvode.CV_BDF, cvode.CV_NEWTON)
rtol = 1e-6
atol = 1e-12
cvode.CVodeMalloc(cvode_mem, cvode_rhs_func, t[0], y, cvode.CV_SS, rtol, atol)
cvode.CVDense(cvode_mem, nspecies)
f_data = ctypes.cast(ctypes.pointer(ctypes.py_object(param_values)), ctypes.c_void_p)
cvode.CVodeSetFdata(cvode_mem, f_data)

yout[0, :nspecies] = y0

def solveit():
    i = 1
    tret = cvode.realtype()
    flag = 0
    while flag >= 0 and tret < t[-1]:
        flag = cvode.CVode(cvode_mem, t[i], y, ctypes.byref(tret), cvode.CV_NORMAL)
        yout[i, :nspecies] = y[:]
        i += 1

def solveit_rep():
    y[:] = y0[:]
    cvode.CVodeReInit(cvode_mem, cvode_rhs_func, t[0], y, cvode.CV_SS, rtol, atol)
    solveit()

if __name__ == '__main__':
    solveit()

    for i, name in enumerate(obs_names):
        factors, species = zip(*model.observable_groups[name])
        yout[:, nspecies + i] = (yout[:, species] * factors).sum(1)

    print 'rhs: ours=%d cvode=%d' % (rhs_count, cvode.CVodeGetNumRhsEvals(cvode_mem))

    p = plot(t, yout / yout.max(0))
    figlegend(p, ['y1', 'y2', 'y3'], 'upper right')
    show()
