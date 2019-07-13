# Created by Gubanov Alexander (aka Derzhiarbuz) at 05.06.2019
# Contacts: derzhiarbuz@gmail.com

from da_icascades_manager import CascadesManager
from da_information_conductivity import InformationConductivity
import numpy as np
import matplotlib.pylab as pl


casman = CascadesManager(name='WorldVita', base_dir='D:/BigData/Charity/Cascades/')
casman.load_from_file()
casman.update_cascades(uselikes=False, usehiddens=False)

cond_net = InformationConductivity()
cond_net.make_cascades_summary(casman.cascades, logweight=False)
cond_net.make_underlying_summary([casman.underlying_net])
# print(cond_net.cascades_network.links)
# print(cond_net.cascades_network.nodes)
# print(cond_net.cascades_network.nodes_attributes)
# print(len(cond_net.underlying.nodes))
# cond_net.cascades_network.export_gexf('D:/BigData/Charity/Cascades/PomogatLegko100Summary.gexf', drop_singletones=True)

summary = cond_net.nodes_summary()
print(summary['in'])
print(len(summary['in']))
print(summary['out'])
print(len(summary['out']))
print(summary['in_w'])
print(len(summary['in_w']))
print(summary['out_w'])
print(len(summary['out_w']))
print(summary['degree'])
print(len(summary['degree']))
print(summary['w'])
print(len(summary['w']))

in_arr = np.array(summary['in'])
out_arr = np.array(summary['out'])
in_w_arr = np.array(summary['in_w'])
out_w_arr = np.array(summary['out_w'])
degree_arr = np.array(summary['degree'])
w_arr = np.array(summary['w'])

# pl.hist(in_arr, bins=np.logspace(np.log10(1), np.log10(np.max(in_arr)), 10))
# pl.gca().set_xscale("log")
# pl.gca().set_yscale("log")
# pl.show()
#
# pl.hist(out_arr, bins=np.logspace(np.log10(1), np.log10(np.max(out_arr)), 10))
# pl.gca().set_xscale("log")
# pl.gca().set_yscale("log")
# pl.show()
#
# pl.hist(in_w_arr, bins=np.logspace(np.log10(1), np.log10(np.max(in_w_arr)), 10))
# pl.gca().set_xscale("log")
# pl.gca().set_yscale("log")
# pl.show()
#
# pl.hist(out_w_arr, bins=np.logspace(np.log10(1), np.log10(np.max(out_w_arr)), 10))
# pl.gca().set_xscale("log")
# pl.gca().set_yscale("log")
# pl.show()

# pl.hist(degree_arr, bins=np.logspace(np.log10(1), np.log10(np.max(degree_arr)), 10))
# pl.gca().set_xscale("log")
# pl.gca().set_yscale("log")
# pl.show()

# pl.hist(w_arr, bins=np.logspace(np.log10(1), np.log10(np.max(w_arr)), 10))
# pl.gca().set_xscale("log")
# pl.gca().set_yscale("log")
# pl.show()

pl.scatter(np.log(out_arr), np.log(in_arr))
pl.show()
