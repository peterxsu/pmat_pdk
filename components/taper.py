# -*- coding: utf-8 -*-
"""
Created on Wed Jul 06 16:45:24 2016

@author: dkita
"""

from gdsCAD import *
from waveguide import WaveguideTemplate
import os
print(os.getcwd())

"""Defines a wrapped ring object.  To use, instantiate the 'cell' property."""

class Taper:
    def __init__(self, name, wg_template1, wg_template2, center=(0,0), taper_len=300.0):
        self.cell = core.Cell(str(name))
        self.portlist = {}
        
        self.center = center
        self.taper_len = taper_len
        self.wg1_width = wg_template1.wg_width
        self.clad1_width = wg_template1.clad_width
        self.wg2_width = wg_template2.wg_width
        self.clad2_width = wg_template2.clad_width
        
        self.wg_layer = wg_template1.wg_layer
        self.clad_layer = wg_template1.clad_layer
        
        self.build_cell()
        self.build_ports()
        
    def build_cell(self):
        """ taper section """
        wl1 = self.wg1_width/2.0
        wl2 = self.wg2_width/2.0
        cl1 = self.clad1_width/2.0
        cl2 = self.clad2_width/2.0
        center = self.center
        
        taper_clad_p = [(center[0] - self.taper_len/2.0, center[1]-cl1),
                        (center[0] - self.taper_len/2.0, center[1]+cl1),
                        (center[0] + self.taper_len/2.0, center[1]+cl2),
                        (center[0] + self.taper_len/2.0, center[1]-cl2)]   
        taper_clad = core.Boundary(taper_clad_p, layer=self.clad_layer)
        self.cell.add(taper_clad)
        
        taper_p = [(center[0] - self.taper_len/2.0, center[1]-wl1),
                        (center[0] - self.taper_len/2.0, center[1]+wl1),
                        (center[0] + self.taper_len/2.0, center[1]+wl2),
                        (center[0] + self.taper_len/2.0, center[1]-wl2)]
        taper = core.Boundary(taper_p, layer=self.wg_layer)
        self.cell.add(taper)
        
        
    def build_ports(self):
        """ Portlist format:  [x_position, y_position, wg_exit_angle] """
        self.portlist["input1"] = [self.center[0]-self.taper_len/2.0, self.center[1], "WEST"]
        self.portlist["input2"] = [self.center[0]+self.taper_len/2.0, self.center[1], "EAST"]
    
if __name__ == "__main__":
    wgt1 = WaveguideTemplate(bend_radius=40.0, wg_width=1.0, clad_width=20.0)
    wgt2 = WaveguideTemplate(bend_radius=40.0, wg_width=10.0, clad_width=30.0)
    t = Taper("taper", wgt1, wgt2)
    t.cell.show()
    print t.portlist