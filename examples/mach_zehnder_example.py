# -*- coding: utf-8 -*-
"""
Created on Tue Jul 05 17:19:22 2016

@author: dkita
"""

from pmat_pdk import *
import pmat_pdk.toolkit as tk

""" Create a top cell """
top = tk.Cell('Top')

""" Create a waveguide template """
wgt = WaveguideTemplate(bend_radius=20.0, wg_width=1.0, clad_width=20.0)

wd = WrappedRing("disk0", wg_template=wgt, center=(0,-400))
tk.rotate(wd, 180)
top.add(wd)

gc = GratingCoupler("gc0", wg_template=wgt, center =(900, 0))
top.add(gc)

gc = GratingCoupler("gc1", wg_template=wgt, center =(-900, 0))
tk.rotate(gc, 180)
top.add(gc)

m1 = MMI1x2("mmi1", wg_template=wgt, center=(-400,0.0))
top.add(m1)
m1 = MMI1x2("mmi2", wg_template=wgt, center=(400,0.0))
tk.rotate(m1, 180)
top.add(m1)

print top.components["mmi1"].portlist["output_bottom"]
netlist = [(top.components["mmi1"].portlist["output_bottom"], top.components["disk0"].portlist["right"]),
           (top.components["gc1"].portlist["input"], top.components["mmi1"].portlist["input"]),
           (top.components["mmi1"].portlist["output_top"], top.components["mmi2"].portlist["output_bottom"]),
           (top.components["disk0"].portlist["left"], top.components["mmi2"].portlist["output_top"]),
           (top.components["mmi2"].portlist["input"], top.components["gc0"].portlist["input"])]

tk.autoBuildWaveguides(top, netlist, wgt)

layout = core.Layout('LIBRARY')
layout.add(top.gdscell)
layout.save('MZI.gds')
os.system('MZI.gds')
layout.show()