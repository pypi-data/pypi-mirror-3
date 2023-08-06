from pysb.integrate import odesolve
from pylab import *

from earm_1_0 import model


t = linspace(0, 6*3600, 6*60+1)  # 6 hours
y = odesolve(model, t)

y_norm = array([y['Bid'], y['PARP'], y['mSmac']]).T
y_norm = 1 - y_norm / y_norm[0, :]  # gets away without max() since first values are largest

tp = t / 3600  # x axis as hours

figure()
plot(tp, y_norm[:,0], 'b', label='IC substrate (tBid)')
plot(tp, y_norm[:,1], 'y', label='EC substrate (cPARP)')
plot(tp, y_norm[:,2], 'r', label='MOMP (cytosolic Smac)')
legend(loc='upper left', bbox_to_anchor=(0,1)).draw_frame(False)
xlabel('Time (hr)')
ylabel('fraction')
a = gca()
a.set_ylim((-.05, 1.05))

show()
