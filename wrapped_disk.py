# -*- coding: utf-8 -*-
"""
Created on Fri Jul 01 12:57:36 2016

@author: dkita
"""

from gdsCAD import *
import os
from components import *
print(os.getcwd())

"""Defines a wrapped disk object.  To use, instantiate the 'cell' property."""

class WrappedDisk:
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
        dc = self.clad_width/2.0
        """ disk """
        dr = self.wg_width/2.0
        disk = shapes.Disk(self.center, self.radius+dr, layer=self.wg_layer)
        disk_c = shapes.Disk(self.center, self.radius+dr+dc, layer=self.clad_layer)
        self.cell.add(disk_c)
        self.cell.add(disk)
        
        """ coupling arc with coupling gap 'cg' """
        rc = self.radius + dr + self.cg + dr
        coupling_arc = shapes.Disk(self.center, rc+dr, inner_radius = rc-dr, initial_angle=0, final_angle=180, layer=self.wg_layer)
        coupling_arc_c = shapes.Disk(self.center, rc+dc, inner_radius = rc-dc, initial_angle=0, final_angle=180, layer=self.clad_layer)
        self.cell.add(coupling_arc_c)
        self.cell.add(coupling_arc)
        
        """ right hand side coupling arc """
        or_r = (self.center[0] + (rc-dr) + (self.radius+dr), self.center[1])
        coupling_arc_r = shapes.Disk(or_r, self.radius+dr, inner_radius = self.radius-dr, initial_angle=270, final_angle=180, layer=self.wg_layer)
        coupling_arc_r_c = shapes.Disk(or_r, self.radius+dc, inner_radius = self.radius-dc, initial_angle=270, final_angle=180, layer=self.clad_layer)
        self.cell.add(coupling_arc_r_c)
        self.cell.add(coupling_arc_r)
        
        """ left hand side coupling arc """
        or_l = (self.center[0] - (rc-dr) - (self.radius+dr), self.center[1])
        coupling_arc_l = shapes.Disk(or_l, self.radius+dr, inner_radius = self.radius-dr, initial_angle=0, final_angle=-90, layer=self.wg_layer)
        coupling_arc_l_c = shapes.Disk(or_l, self.radius+dc, inner_radius = self.radius-dc, initial_angle=0, final_angle=-90, layer=self.clad_layer)
        self.cell.add(coupling_arc_l_c)
        self.cell.add(coupling_arc_l)
        
    def build_ports(self):
        """ Portlist format:  [x_position, y_position, wg_exit_angle] """
        dr = self.wg_width/2.0
        rc = self.radius + dr + self.cg + dr
        self.portlist["left"] = [self.center[0] - (rc-dr) - (self.radius+dr), self.center[1] - self.radius, "WEST"]
        self.portlist["right"] = [self.center[0] + (rc-dr) + (self.radius+dr), self.center[1] - self.radius, "EAST"]
    
if __name__ == "__main__":
    wgt = WaveguideTemplate(bend_radius=50, wg_width=1.3, clad_width=20)
    wr = WrappedDisk("d1", wg_template=wgt)
    wr.cell.show()