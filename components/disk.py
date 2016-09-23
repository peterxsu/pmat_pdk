# -*- coding: utf-8 -*-
"""
Created on Fri Jul 01 12:57:36 2016

@author: dkita
"""

from gdsCAD import *
from components import *
import os
print(os.getcwd())

"""Defines a wrapped disk object.  To use, instantiate the 'cell' property."""

class Disk:
    def __init__(self, name, wg_template, center=(0,0), radius=50.0, cg=1.0):
        self.cell = core.Cell(str(name))
        self.portlist = {}
        
        self.center = center
        self.radius = radius
        self.bend_radius = wg_template.bend_radius
        self.wg_width = wg_template.wg_width
        self.clad_width = wg_template.clad_width
        self.cg = cg
        
        self.wg_layer = wg_template.wg_layer
        self.clad_layer = wg_template.clad_layer
        
        self.build_cell()
        self.build_ports()
        
    def build_cell(self):
        dc = self.clad_width/2.0 - self.wg_width/2.0
        """ disk """
        disk = shapes.Disk(self.center, self.radius, layer=self.wg_layer)
        disk_c = shapes.Disk(self.center, self.radius+dc, layer=self.clad_layer)
        
        """ bus wg with coupling gap 'cg' """
        wg_bottom_y = self.center[1]+self.radius+self.cg
        buswg = shapes.Rectangle((-2.0*self.radius+self.center[0], wg_bottom_y), (2.0*self.radius + self.center[0], wg_bottom_y+self.wg_width), layer=self.wg_layer)
        buswg_c = shapes.Rectangle((-2.0*self.radius+self.center[0], wg_bottom_y - dc), (2.0*self.radius+self.center[0], wg_bottom_y + self.wg_width + dc), layer=self.clad_layer)        
        
        """ objects to the cell, cladding first so it is in background of matplotlib img """
        self.cell.add(buswg_c)
        self.cell.add(disk_c)
        self.cell.add(buswg)
        self.cell.add(disk)
        
    def build_ports(self):
        """ Portlist format:  [x_position, y_position, wg_exit_angle] """
        self.portlist["left"] = [-2.0*self.radius+self.center[0], self.center[1]+self.radius+self.cg + self.wg_width/2.0, "WEST"]
        self.portlist["right"] = [2.0*self.radius+self.center[0], self.center[1]+self.radius+self.cg + self.wg_width/2.0, "EAST"]
    
if __name__ == "__main__":
    wgt = WaveguideTemplate(bend_radius=100.0, wg_width=2.0, clad_width=22.0)

    d = Disk("d1", wgt)
    print d.portlist
    d.cell.show()