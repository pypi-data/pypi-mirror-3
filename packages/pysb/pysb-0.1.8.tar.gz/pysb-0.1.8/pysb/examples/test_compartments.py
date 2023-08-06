from pysb import *
import logging

logging.basicConfig()
complog = logging.getLogger("compartments_file")
#complog.setLevel(logging.DEBUG)

complog.debug("starting Model")
Model()

complog.debug("setting Compartment")
Parameter('ec_size', 11);
Parameter('ec_mem_size', 7)
Parameter('cyto_size', 5)
Parameter('endo_mem_size', 3)
Compartment('extra_cellular', dimension=3, size=ec_size,   parent=None)
Compartment('ec_membrane', dimension=2, size=ec_mem_size, parent=extra_cellular)
Compartment('cytoplasm', dimension=3, size=cyto_size, parent=ec_membrane)
Compartment('endo_membrane', dimension=2, size=endo_mem_size, parent=cytoplasm)
Compartment('endosome', dimension=3, parent=endo_membrane) # test default size of 1.0


complog.debug("setting Monomers")
Monomer('egf', ['R','test'], {'test':['up', 'down']})
Monomer('egfr', ['L', 'D', 'C'], {'C':['on', 'off']})
Monomer('shc', ['L', 'A'], {'A':['on', 'off']})

Parameter('K_egfr_egf_F', 1.2e-6)
Parameter('K_egfr_egf_R', 1.2e-8)
Rule('egfr_egf',
     egfr(L=None) + egf(R=None) <>
     egfr(L=1)    % egf(R=1),
     K_egfr_egf_F, K_egfr_egf_R)

Parameter('K_egfr_endo', 5e-4)
Rule('egfr_endocytosis',
     (egfr(L=1) % egf(R=1)) ** ec_membrane >>
     (egfr(L=1) % egf(R=1)) ** endo_membrane,
     K_egfr_endo)

Observable('egfr_total', egfr())
Observable('egfr_egf_endo', (egfr(L=1) % egf(R=1)) ** endo_membrane)
Observable('egfr_ec_mem', (egfr(L=1) % egf(R=1)) ** ec_membrane)
Observable('egfr_unbound', egfr(L=None))

Parameter('egf_0', 1e4)
Parameter('egfr_0', 5e2)
Initial(egf(R=None, test='up') ** extra_cellular, egf_0)
Initial(egfr(L=None, D=None, C='off') ** ec_membrane, egfr_0)


#####

if __name__ == '__main__':
    from pysb.integrate import odesolve
    from pylab import *

    t = linspace(0, 21600, 200)
    y = odesolve(model, t)

    plot(t, array([y['egfr_total'], y['egfr_egf_endo'], y['egfr_ec_mem'], y['egfr_unbound']]).T)
    ylim(0, 510)
    show()
