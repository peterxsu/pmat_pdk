# -*- coding: utf-8 -*-
"""
Created on Tue Jul 05 12:33:36 2016

@author: dkita
"""

from gdsCAD import *
from waveguide import WaveguideTemplate
import os
print(os.getcwd())

"""Defines a wrapped ring object.  To use, instantiate the 'cell' property."""

class GratingCoupler:
    def __init__(self, name, wg_template, center=(0,0), period=1.16, duty_cycle = 0.5, width=20.0, length=75.0, taper_len=300.0):
        self.cell = core.Cell(str(name))
        self.portlist = {}
        
        self.center = center
        self.period = period
        self.duty_cycle = duty_cycle
        self.width = width
        self.length = length
        self.taper_len = taper_len
        self.wg_width = wg_template.wg_width
        self.clad_width = wg_template.clad_width
        
        self.build_cell()
        self.build_ports()
        
    def build_cell(self):
        """ grating """
        center = (self.center[0]+self.taper_len/2.0, self.center[1])
        dc = self.clad_width/2.0
        lower_left = [center[0] - self.length/2.0, center[1]-self.width/2.0]
        upper_right = [center[0]+self.length/2.0, center[1]+self.width/2.0]
        
        gc_clad = shapes.Rectangle((lower_left[0]-dc, lower_left[1]-dc), (upper_right[0]+dc, upper_right[1]+dc), layer=2)
        self.cell.add(gc_clad)
        
        num_rects = int(self.length/self.period)
        for i in xrange(num_rects):
            r = shapes.Rectangle((lower_left[0]+i*self.period, lower_left[1]), (lower_left[0]+self.duty_cycle*self.period + i*self.period, upper_right[1]), layer=1)
            self.cell.add(r)
            
        """ taper """
        taper_clad_p = [(lower_left[0]-dc, lower_left[1]-dc),
                        (lower_left[0]-dc, upper_right[1]+dc),
                        (lower_left[0]-self.taper_len, center[1]+dc),
                        (lower_left[0]-self.taper_len, center[1]-dc)]   
        taper_clad = core.Boundary(taper_clad_p, layer=2)
        self.cell.add(taper_clad)
        
        taper_p = [(lower_left[0] + self.duty_cycle*self.period, lower_left[1]),
                    (lower_left[0] + self.duty_cycle*self.period, upper_right[1]),
                    (lower_left[0]-self.taper_len, center[1]+self.wg_width/2.0),
                    (lower_left[0]-self.taper_len, center[1]-self.wg_width/2.0)]
        taper = core.Boundary(taper_p, layer=1)
        self.cell.add(taper)
        
        
    def build_ports(self):
        center = (self.center[0]+self.taper_len/2.0, self.center[1])
        """ Portlist format:  [x_position, y_position, wg_exit_angle] """
        self.portlist["input"] = [center[0] - self.length/2.0 - self.taper_len, center[1], "WEST"]
    
if __name__ == "__main__":
    wgt = WaveguideTemplate(bend_radius=40.0, wg_width=1.0, clad_width=20.0)
    gc = GratingCoupler("gc", wgt)
    gc.cell.show()
    print gc.portlist