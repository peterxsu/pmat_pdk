# -*- coding: utf-8 -*-
"""
Created on Fri Jul 01 13:06:48 2016

@author: dkita
"""

import os.path
from components import *
import PDKtoolkit as tk
from gdsCAD import *

""" Create a top cell """
top = tk.Cell('Top')

""" Create a waveguide template """
wgt = WaveguideTemplate(bend_radius=40.0, wg_width=1.0, clad_width=20.0)

#for i in xrange(3):
#    wd = WrappedRing("disk"+str(i), wg_template=wgt, center=(0,500*i))
#    top.add(wd)
#
#netlist = [(top.components["disk0"].portlist["left"], top.components["disk1"].portlist["left"]),
#           (top.components["disk1"].portlist["right"], top.components["disk2"].portlist["right"]),
#           (top.components["disk0"].portlist["right"], top.components["disk2"].portlist["left"])]

wd = WrappedDisk("disk0", wg_template=wgt, center=(0,500))
top.add(wd)
wd = WrappedDisk("disk1", wg_template=wgt, center=(300,1550))
tk.rotate(wd, -90)
print wd.portlist
top.add(wd)
wd = WrappedDisk("disk2", wg_template=wgt, center=(300,0))
top.add(wd)
gc = GratingCoupler("gc0", wg_template=wgt, center =(1200, 200))
top.add(gc)
gc = GratingCoupler("gc1", wg_template=wgt, center =(-500, 0))
tk.rotate(gc, 180)
top.add(gc)

    
netlist = [(top.components["gc0"].portlist["input"], top.components["disk2"].portlist["right"]),
           (top.components["gc1"].portlist["input"], top.components["disk0"].portlist["right"]),
           (top.components["disk2"].portlist["left"], top.components["disk1"].portlist["right"]),
           (top.components["disk0"].portlist["left"], top.components["disk1"].portlist["left"])]
#
#netlist = [(top.components["gc0"].portlist["input"], top.components["disk2"].portlist["right"]),
#           (top.components["gc1"].portlist["input"], top.components["disk0"].portlist["right"])]

tk.autoBuildWaveguides(top, netlist, wgt)
#print top.cell.elements

layout = core.Layout('LIBRARY')
layout.add(top.gdscell)    
layout.save('output.gds')
os.system('output.gds')
layout.show()