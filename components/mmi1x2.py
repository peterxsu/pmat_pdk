# -*- coding: utf-8 -*-
"""
Created on Tue Jul 05 17:46:53 2016

@author: dkita
"""
from waveguide import WaveguideTemplate
from gdsCAD import *
import os
print(os.getcwd())

"""Defines a 1x2 MMI.  To use, instantiate the 'cell' property."""

class MMI1x2:
    def __init__(self, name, wg_template, center=(0,0), length=33.0, width=7.5, offset = 2.0):
        self.cell = core.Cell(str(name))
        self.portlist = {}
        
        self.center = center
        self.wg_width = wg_template.wg_width
        self.clad_width = wg_template.clad_width
        self.length = length
        self.width = width
        self.offset = offset
        
        self.build_cell()
        self.build_ports()
        
    def build_cell(self):
        """ Multimode interferometer """
        mr_c = shapes.Rectangle((self.center[0]-self.length/2.0-self.clad_width/2.0, self.center[1]-self.width/2.0-self.clad_width/2.0), 
                              (self.center[0]+self.length/2.0+self.clad_width/2.0, self.center[1]+self.width/2.0+self.clad_width/2.0), layer=2)
        self.cell.add(mr_c)
        mr = shapes.Rectangle((self.center[0]-self.length/2.0, self.center[1]-self.width/2.0), 
                              (self.center[0]+self.length/2.0, self.center[1]+self.width/2.0), layer=1)
        self.cell.add(mr)
        
        
    def build_ports(self):
        """ Portlist format:  [x_position, y_position, wg_exit_angle] """
        print "Building ports at center: "+str(self.center)
        self.portlist["output_top"] = [self.center[0]+self.length/2.0, self.center[1]+self.offset, "EAST"]
        self.portlist["output_bottom"] = [self.center[0]+self.length/2.0, self.center[1]-self.offset, "EAST"]
        self.portlist["input"] = [self.center[0]-self.length/2.0, self.center[1], "WEST"]
    
if __name__ == "__main__":
    wgt = WaveguideTemplate(bend_radius=40.0, wg_width=1.0, clad_width=20.0)
    mmi = MMI1x2("mmi1", wgt)
    print mmi.portlist
    mmi.cell.show()