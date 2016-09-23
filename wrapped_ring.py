# -*- coding: utf-8 -*-
"""
Created on Fri Jul 01 11:54:57 2016

@author: dkita
"""

from gdsCAD import *
from components import *
import os
print(os.getcwd())

"""Defines a wrapped ring object.  To use, instantiate the 'cell' property."""

class WrappedRing:
    def __init__(self, name, wg_template, center=(0,0), radius=50.0, cg=1.0):
        self.cell = core.Cell(str(name))
        self.portlist = {}
        
        self.center = center
        self.radius = radius
        self.bend_radius = wg_template.bend_radius
        self.wg_width = wg_template.wg_width
        self.clad_width = wg_template.clad_width
        self.cg = cg
        
        self.build_cell()
        self.build_ports()
        
    def build_cell(self):
        dc = self.clad_width/2.0
        """ ring """
        dr = self.wg_width/2.0
        ring = shapes.Disk(self.center, self.radius+dr, inner_radius=self.radius-dr, layer=1)
        ring_c = shapes.Disk(self.center, self.radius+dr+dc, inner_radius=self.radius-dr-dc, layer=2)
        self.cell.add(ring_c)
        self.cell.add(ring)
        
        """ coupling arc with coupling gap 'cg' """
        rc = self.radius + dr + self.cg + dr
        coupling_arc = shapes.Disk(self.center, rc+dr, inner_radius = rc-dr, initial_angle=0, final_angle=180, layer=1)
        coupling_arc_c = shapes.Disk(self.center, rc+dc, inner_radius = rc-dc, initial_angle=0, final_angle=180, layer=2)
        self.cell.add(coupling_arc_c)
        self.cell.add(coupling_arc)
        
        """ right hand side coupling arc """
        or_r = (self.center[0] + (rc-dr) + (self.radius+dr), self.center[1])
        coupling_arc_r = shapes.Disk(or_r, self.radius+dr, inner_radius = self.radius-dr, initial_angle=270, final_angle=180, layer=1)
        coupling_arc_r_c = shapes.Disk(or_r, self.radius+dc, inner_radius = self.radius-dc, initial_angle=270, final_angle=180, layer=2)
        self.cell.add(coupling_arc_r_c)
        self.cell.add(coupling_arc_r)
        
        """ left hand side coupling arc """
        or_l = (self.center[0] - (rc-dr) - (self.radius+dr), self.center[1])
        coupling_arc_l = shapes.Disk(or_l, self.radius+dr, inner_radius = self.radius-dr, initial_angle=0, final_angle=-90, layer=1)
        coupling_arc_l_c = shapes.Disk(or_l, self.radius+dc, inner_radius = self.radius-dc, initial_angle=0, final_angle=-90, layer=2)
        self.cell.add(coupling_arc_l_c)
        self.cell.add(coupling_arc_l)
        
    def build_ports(self):
        """ Portlist format:  [x_position, y_position, wg_exit_angle] """
        dr = self.wg_width/2.0
        rc = self.radius + dr + self.cg + dr
        self.portlist["left"] = [self.center[0] - (rc-dr) - (self.radius+dr), self.center[1] - self.radius, "WEST"]
        self.portlist["right"] = [self.center[0] + (rc-dr) + (self.radius+dr), self.center[1] - self.radius, "EAST"]
    
if __name__ == "__main__":
    wgt = WaveguideTemplate(bend_radius=100.0, wg_width=2.0, clad_width=22.0)
    
    wr = WrappedRing("r1", wgt)
    wr.cell.show()