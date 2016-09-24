# -*- coding: utf-8 -*-
"""
Created on Sat Sep 24 16:28:33 2016

@author: dkita
"""

from pmat_pdk import *
import pmat_pdk.toolkit as tk

top = tk.Cell('Top')

wgt = WaveguideTemplate(bend_radius=20.0, wg_width=0.7, clad_width=10.0)

gc1 = GratingCoupler("gc1", wg_template=wgt, center =(-300, -225))
tk.rotate(gc1, 180)
gc2 = GratingCoupler("gc2", wg_template=wgt, center =(300, 225))

top.add(gc1)
top.add(gc2)

x_start = top.components["gc1"].portlist["input"][0]
y_start = top.components["gc1"].portlist["input"][1]
x_end = top.components["gc2"].portlist["input"][0]
y_end = top.components["gc2"].portlist["input"][1]
tracelist = []
tracelist.append([[x_start, y_start], [(x_start + x_end)/2.0, y_start], [(x_start + x_end)/2.0, y_end], [x_end, y_end]])

tk.buildWaveguides(top, tracelist, wgt)

layout = core.Layout('LIBRARY')
layout.add(top.gdscell)
layout.save('first_mask2.gds')
os.system('first_mask2.gds')
layout.show()