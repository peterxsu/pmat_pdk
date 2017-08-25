# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 22:12:30 2016

@author: Peter
"""

from gdsCAD import *
from waveguide import WaveguideTemplate
import os
import math

"""Defines a spiral waveguide object.  To use, instantiate the 'cell' property."""

class SpiralWaveguide:
    def __init__(self, name, wg_template, center=(0,0), min_spiral_length=10000.0, max_spiral_width=1000.0):
        self.cell = core.Cell(str(name))
        self.portlist = {}
        
        self.center = center
        
        self.min_spiral_length = min_spiral_length
        self.max_spiral_width = max_spiral_width
        self.wg_width = wg_template.wg_width
        self.clad_width = wg_template.clad_width
        self.bend_radius = wg_template.bend_radius
        
        self.real_length = min_spiral_length
        
        self.build_cell()
        self.build_ports()
        
    def build_cell(self):
        """ calculate spiral parameters """
        br = self.bend_radius
        cw = self.clad_width
        a = math.pi*cw
        b = 4*math.pi*br
        c = 2*math.pi*br - self.min_spiral_length
        num_circles = int(math.ceil((-b + math.sqrt(b**2 - 4*a*c))/(2*a)))
        if num_circles < 0: num_circles = 0
        if 6*br + 2*num_circles*cw > self.max_spiral_width:
            raise ValueError("min_spiral_length too large for max_spiral_width")
        else:
            self.real_length = a*num_circles**2 + b*num_circles + c + self.min_spiral_length
            print("The real length of the spiral is about: "+str(self.real_length))
            center = self.center
            """ cladding """
            spiral_clad = shapes.Rectangle((center[0]-(3*br+cw*num_circles), center[1]-(2*br+cw*num_circles+cw/2)), (center[0]+(3*br+cw*num_circles), center[1]+(2*br+cw*num_circles+cw/2)), layer=2)
            input_clad = shapes.Rectangle((center[0]-self.max_spiral_width/2, center[1]-cw/2), (center[0]-(3*br+cw*num_circles), center[1]+cw/2), layer=2)
            output_clad = shapes.Rectangle((center[0]+self.max_spiral_width/2, center[1]+cw/2), (center[0]+(3*br+cw*num_circles), center[1]-cw/2), layer=2)
            
            self.cell.add(input_clad)
            self.cell.add(spiral_clad)
            self.cell.add(output_clad)
            
            """ spiral """
            wg_width = self.wg_width
            angle_correction = 0
            real_spiral_width = br + br*math.sqrt(3)
            if num_circles == 0:
                angle_correction = 30
                arc_left = shapes.Disk((center[0]-br,center[1]), br+wg_width/2, inner_radius=br-wg_width/2, initial_angle=0, final_angle=180-angle_correction, layer=1)
                arc_right = shapes.Disk((center[0]+br,center[1]), br+wg_width/2, inner_radius=br-wg_width/2, initial_angle=180, final_angle=360-angle_correction, layer=1)
                
                self.cell.add(arc_left)
                self.cell.add(arc_right)
                
                real_spiral_width = br + br*math.sqrt(3)
            else:
                center_left = (center[0]-cw/2,center[1])
                center_right = (center[0]+cw/2,center[1])
                for i in range(num_circles,0,-1):
                    arc_radius = 2*br + (2*i-1)*cw/2
                    arc_outer_radius = arc_radius + wg_width/2
                    arc_inner_radius = arc_radius - wg_width/2
                    if i == num_circles:
                        angle_correction = math.asin(br/(br+arc_radius))*180/math.pi
                        arc_left = shapes.Disk(center_left, arc_outer_radius, inner_radius=arc_inner_radius, initial_angle=0, final_angle=180-angle_correction, layer=1)
                        arc_right = shapes.Disk(center_right, arc_outer_radius, inner_radius=arc_inner_radius, initial_angle=180, final_angle=360-angle_correction, layer=1)
                        
                        self.cell.add(arc_left)
                        self.cell.add(arc_right)
                    else:
                        arc_left = shapes.Disk(center_left, arc_outer_radius, inner_radius=arc_inner_radius, initial_angle=0, final_angle=180, layer=1)
                        arc_right = shapes.Disk(center_right, arc_outer_radius, inner_radius=arc_inner_radius, initial_angle=180, final_angle=360, layer=1)
                        
                        self.cell.add(arc_left)
                        self.cell.add(arc_right)
                arc_left = shapes.Disk((center[0]-br,center[1]), br+wg_width/2, inner_radius=br-wg_width/2, initial_angle=0, final_angle=180, layer=1)
                arc_right = shapes.Disk((center[0]+br,center[1]), br+wg_width/2, inner_radius=br-wg_width/2, initial_angle=180, final_angle=360, layer=1)
                
                self.cell.add(arc_left)
                self.cell.add(arc_right)
                
                real_spiral_width = math.sqrt((3*br+cw*num_circles-cw/2)**2 - br**2) + cw/2
            
            """ input and output waveguides """
            input_wg = shapes.Rectangle((center[0]-self.max_spiral_width/2, center[1]-wg_width/2), (center[0]-real_spiral_width, center[1]+wg_width/2), layer=1)
            output_wg = shapes.Rectangle((center[0]+self.max_spiral_width/2, center[1]+wg_width/2), (center[0]+real_spiral_width, center[1]-wg_width/2), layer=1)
            input_connecting_arc = shapes.Disk((center[0]-real_spiral_width,center[1]+br), br+wg_width/2, inner_radius=br-wg_width/2, initial_angle=270, final_angle=360-angle_correction, layer=1)
            output_connecting_arc = shapes.Disk((center[0]+real_spiral_width,center[1]-br), br+wg_width/2, inner_radius=br-wg_width/2, initial_angle=90, final_angle=180-angle_correction, layer=1)
            
            self.cell.add(input_wg)
            self.cell.add(input_connecting_arc)
            self.cell.add(output_connecting_arc)
            self.cell.add(output_wg)
        
    def build_ports(self):
        """ Portlist format:  [x_position, y_position, wg_exit_angle] """
        self.portlist["input"] = [self.center[0]-self.max_spiral_width/2, self.center[1], "WEST"]
        self.portlist["output"] = [self.center[0]+self.max_spiral_width/2, self.center[1], "EAST"]
    
"""Defines a spiral waveguide core object for use with offset structures that want to minimize bends.  To use, instantiate the 'cell' property."""

class SpiralWaveguideCore:
    def __init__(self, name, wg_template, center=(0,0), min_spiral_length=10000.0, max_spiral_width=1000.0):
        self.cell = core.Cell(str(name))
        self.portlist = {}
        
        self.center = center
        
        self.min_spiral_length = min_spiral_length
        self.max_spiral_width = max_spiral_width
        self.wg_width = wg_template.wg_width
        self.clad_width = wg_template.clad_width
        self.bend_radius = wg_template.bend_radius
        
        self.real_length = min_spiral_length
        
        self.build_cell()
        self.build_ports()
        
    def build_cell(self):
        """ calculate spiral parameters """
        br = self.bend_radius
        cw = self.clad_width
        a = math.pi*cw
        b = 4*math.pi*br
        c = 2*math.pi*br - self.min_spiral_length
        num_circles = int(math.ceil((-b + math.sqrt(b**2 - 4*a*c))/(2*a)))
        if num_circles < 0: num_circles = 0
        if 6*br + 2*num_circles*cw > self.max_spiral_width:
            raise ValueError("min_spiral_length too large for max_spiral_width")
        else:
            self.real_length = a*num_circles**2 + b*num_circles + c + self.min_spiral_length
            print("The real length of the spiral is about: "+str(self.real_length))
            center = self.center
            """ cladding """
            spiral_width = 4*br + 2*cw*(num_circles+1)
            spiral_clad = shapes.Rectangle((center[0]-spiral_width/2, center[1]-spiral_width/2), (center[0]+spiral_width/2, center[1]+spiral_width/2), layer=2)
            
            self.cell.add(spiral_clad)
            
            """ spiral """
            wg_width = self.wg_width
            center_left = (center[0]-cw/2,center[1])
            center_right = (center[0]+cw/2,center[1])
            for i in range(num_circles,0,-1):
                arc_radius = 2*br + (2*i-1)*cw/2
                arc_outer_radius = arc_radius + wg_width/2
                arc_inner_radius = arc_radius - wg_width/2
                arc_left = shapes.Disk(center_left, arc_outer_radius, inner_radius=arc_inner_radius, initial_angle=0, final_angle=180, layer=1)
                arc_right = shapes.Disk(center_right, arc_outer_radius, inner_radius=arc_inner_radius, initial_angle=180, final_angle=360, layer=1)
                
                self.cell.add(arc_left)
                self.cell.add(arc_right)
                
            arc_left = shapes.Disk((center[0]-br,center[1]), br+wg_width/2, inner_radius=br-wg_width/2, initial_angle=0, final_angle=180, layer=1)
            arc_right = shapes.Disk((center[0]+br,center[1]), br+wg_width/2, inner_radius=br-wg_width/2, initial_angle=180, final_angle=360, layer=1)
            
            self.cell.add(arc_left)
            self.cell.add(arc_right)
        
    def build_ports(self):
        """ Portlist format:  [x_position, y_position, wg_exit_angle] """
        br = self.bend_radius
        cw = self.clad_width
        a = math.pi*cw
        b = 4*math.pi*br
        c = 2*math.pi*br - self.min_spiral_length
        num_circles = int(math.ceil((-b + math.sqrt(b**2 - 4*a*c))/(2*a)))
        if num_circles < 0: num_circles = 0
        
        self.portlist["input"] = [self.center[0]-(2*br+cw*num_circles), self.center[1], "SOUTH"]
        self.portlist["output"] = [self.center[0]+(2*br+cw*num_circles), self.center[1], "NORTH"]

if __name__ == "__main__":
    wgt = WaveguideTemplate(bend_radius=100.0, wg_width=2.0, clad_width=20.0)
    swg = SpiralWaveguideCore("gc", wgt, min_spiral_length=1000.0, max_spiral_width=1000.0)
    swg.cell.show()
    print swg.portlist