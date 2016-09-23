# -*- coding: utf-8 -*-
"""
Created on Mon Aug 01 14:26:53 2016

@author: dkita
"""

import os.path

from PMAT_PDK.components import *
from PMAT_PDK import PDKtoolkit as tk
from gdsCAD import *

""" Create a top cell """
top = tk.Cell('Top')

""" Create a waveguide templates"""
wgt = WaveguideTemplate(bend_radius=100.0, wg_width=1.3, clad_width=21.3)
tpt = WaveguideTemplate(bend_radius=100.0, wg_width=2.5, clad_width=21.5)
alignment_wgt = WaveguideTemplate(bend_radius=200.0, wg_width=10.0, clad_width=30.0)

num_rings = 20
space = 200.0
space_x = 75.0
for i in xrange(num_rings):
    cg = i*0.05 + 0.05
    wd = Disk("disk"+str(i), wg_template=wgt, center=(i*space,i*space), radius = 50.0, cg = cg)
    top.add(wd)
    top.add_individual(shapes.Label('CG='+str(cg)+"um", 20, (i*space + 250.0,i*space-25.0)))
    tp = Taper("taper_top"+str(i), wgt, tpt, center=(num_rings*space+250 + i*space_x, num_rings*space+300))
    tk.rotate(tp, 90)
    top.add(tp)
    tp = Taper("taper_bot"+str(i), wgt, tpt, center=(-250 - (i+1)*space_x, -500))
    tk.rotate(tp, -90)
    top.add(tp)
    
top.add(AlignmentMarker("upper_right", center=(num_rings*space+250 + num_rings*space_x + space + 100.0, num_rings*space+300), layer_hole=5))
top.add(AlignmentMarker("lower_right", center=(num_rings*space+250 + num_rings*space_x + space + 100.0, -500), layer_hole=5))
top.add(AlignmentMarker("upper_left", center=(-250 - (num_rings+1)*space_x-space - 100.0, num_rings*space+300), layer_hole=5))
top.add(AlignmentMarker("lower_right", center=(-250 - (num_rings+1)*space_x-space - 100.0, -500), layer_hole=5))
    
tracelist = []
for i in xrange(num_rings):
    tracelist.append([[top.components["disk"+str(i)].portlist["right"][0], top.components["disk"+str(i)].portlist["right"][1]],
                      [top.components["taper_top"+str(num_rings-i-1)].portlist["input1"][0], top.components["disk"+str(i)].portlist["right"][1]],
                      [top.components["taper_top"+str(num_rings-i-1)].portlist["input1"][0], top.components["taper_top"+str(num_rings-i-1)].portlist["input1"][1]]])
    tracelist.append([[top.components["disk"+str(i)].portlist["left"][0], top.components["disk"+str(i)].portlist["left"][1]],
                      [top.components["taper_bot"+str(i)].portlist["input1"][0], top.components["disk"+str(i)].portlist["left"][1]],
                      [top.components["taper_bot"+str(i)].portlist["input1"][0], top.components["taper_bot"+str(i)].portlist["input1"][1]]])
tk.buildWaveguides(top, tracelist, wgt)
    
tracelist = []
y_top = 0.0
y_bot = 0.0
for i in xrange(num_rings):
    port = top.components["taper_top"+str(i)].portlist["input2"]
    tracelist.append([[port[0], port[1]], [port[0], port[1]+6000.0]])
    y_top = port[1]+6000.0
    port = top.components["taper_bot"+str(i)].portlist["input2"]
    tracelist.append([[port[0], port[1]], [port[0], port[1]-6000.0]])
    y_bot = port[1]-6000.0
    
tk.buildWaveguides(top, tracelist, tpt)

tracelist = []
tracelist.append([[num_rings*space+250 + num_rings*space_x, y_bot], [num_rings*space+250 + num_rings*space_x, y_top]])
tracelist.append([[-250 - (num_rings+1)*space_x, y_bot], [-250 - (num_rings+1)*space_x, y_top]])
tk.buildWaveguides(top, tracelist, alignment_wgt)
    
    
layout = core.Layout('LIBRARY')
layout.add(top.gdscell)    
layout.save('disk_array.gds')
os.system('disk_array.gds')
layout.show()