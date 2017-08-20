# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 22:12:30 2016

@author: Peter
"""

from gdsCAD import *
from waveguide import WaveguideTemplate
import os
import math

"""Defines an s-bend waveguide object.  To use, instantiate the 'cell' property."""

class SBend:
    def __init__(self, name, wg_template, start=(0,0), delta_y=10.0):
        self.cell = core.Cell(str(name))
        self.portlist = {}
        
        self.start = start
        self.delta_y = delta_y
        
        self.wg_width = wg_template.wg_width
        self.clad_width = wg_template.clad_width
        self.bend_radius = wg_template.bend_radius
        
        if abs(delta_y) > 2*self.bend_radius:
            self.length = 2*self.bend_radius
        else:
            self.length = 2*math.sqrt(self.bend_radius**2-(self.bend_radius-abs(delta_y)/2)**2)
        
        self.build_cell()
        self.build_ports()
        
    def build_cell(self):
        """ calculate spiral parameters """
        br = self.bend_radius
        cw = self.clad_width
        wg_width = self.wg_width
        delta_y = self.delta_y
        start = self.start
        length = self.length
        
        if abs(delta_y) > 2*br:
            angle = 90
        else:
            angle = math.acos((br-abs(delta_y)/2)/br)*180/math.pi
        
        """ cladding """
        if delta_y > 0:
            input_clad_arc = shapes.Disk((start[0],start[1]+br), br+cw/2, inner_radius=br-cw/2, initial_angle=270, final_angle=270+angle, layer=2)
            output_clad_arc = shapes.Disk((start[0]+length,start[1]+delta_y-br), br+cw/2, inner_radius=br-cw/2, initial_angle=90, final_angle=90+angle, layer=2)
        else:
            input_clad_arc = shapes.Disk((start[0],start[1]-br), br+cw/2, inner_radius=br-cw/2, initial_angle=90, final_angle=90-angle, layer=2)
            output_clad_arc = shapes.Disk((start[0]+length,start[1]+delta_y+br), br+cw/2, inner_radius=br-cw/2, initial_angle=270, final_angle=270-angle, layer=2)
        
        self.cell.add(input_clad_arc)
        self.cell.add(output_clad_arc)
        
        if abs(delta_y) > 2*br:
            straight_clad_wg = shapes.Rectangle((start[0]+br-cw/2,start[1]+math.copysign(br,delta_y)), (start[0]+br+cw/2,start[1]+delta_y-math.copysign(br,delta_y)), layer=2)
            self.cell.add(straight_clad_wg)
        
        """ s-bend """
        if delta_y > 0:
            input_arc = shapes.Disk((start[0],start[1]+br), br+wg_width/2, inner_radius=br-wg_width/2, initial_angle=270, final_angle=270+angle, layer=1)
            output_arc = shapes.Disk((start[0]+length,start[1]+delta_y-br), br+wg_width/2, inner_radius=br-wg_width/2, initial_angle=90, final_angle=90+angle, layer=1)
        else:
            input_arc = shapes.Disk((start[0],start[1]-br), br+wg_width/2, inner_radius=br-wg_width/2, initial_angle=90, final_angle=90-angle, layer=1)
            output_arc = shapes.Disk((start[0]+length,start[1]+delta_y+br), br+wg_width/2, inner_radius=br-wg_width/2, initial_angle=270, final_angle=270-angle, layer=1)
        
        self.cell.add(input_arc)
        self.cell.add(output_arc)
        
        if abs(delta_y) > 2*br:
            straight_wg = shapes.Rectangle((start[0]+br-wg_width/2,start[1]+math.copysign(br,delta_y)), (start[0]+br+wg_width/2,start[1]+delta_y-math.copysign(br,delta_y)), layer=1)
            self.cell.add(straight_wg)
        
    def build_ports(self):
        """ Portlist format:  [x_position, y_position, wg_exit_angle] """
        self.portlist["input1"] = [self.start[0], self.start[1], "WEST"]
        self.portlist["input2"] = [self.start[0]+self.length, self.start[1]+self.delta_y, "EAST"]

if __name__ == "__main__":
    wgt = WaveguideTemplate(bend_radius=100.0, wg_width=2.0, clad_width=20.0)
    swg = SBend("sb", wgt, delta_y=1000.0)
    swg.cell.show()
    print swg.portlist