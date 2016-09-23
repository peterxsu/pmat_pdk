# -*- coding: utf-8 -*-
"""
Created on Mon Aug 01 17:17:54 2016

@author: dkita
"""

from gdsCAD import *
from waveguide import WaveguideTemplate
import os
print(os.getcwd())

"""Defines a wrapped ring object.  To use, instantiate the 'cell' property."""

class AlignmentMarker:
    def __init__(self, name, center=(0,0), layer_main=1, layer_hole=2):
        self.cell = core.Cell(str(name))
        self.center = center
        self.layer_main = layer_main
        self.layer_hole = layer_hole        
        
        self.build_cell()
        
    def build_cell(self):
        """ taper section """
        big_cross_width = 2.0
        big_cross_length = 300.0
        little_cross_width = 0.5
        center = self.center
        
        cross_horizontal_p_l = [(center[0] - big_cross_length/2.0, center[1]-big_cross_width/2.0),
                        (center[0] - big_cross_length/2.0, center[1]+big_cross_width/2.0),
                        (center[0] - big_cross_width, center[1]+big_cross_width/2.0),
                        (center[0] - big_cross_width, center[1]-big_cross_width/2.0)]   
        cross_horizontal_l = core.Boundary(cross_horizontal_p_l, layer=self.layer_main)
        self.cell.add(cross_horizontal_l)
        
        cross_horizontal_p_r = [(center[0] + big_cross_width, center[1]-big_cross_width/2.0),
                        (center[0] +big_cross_width, center[1]+big_cross_width/2.0),
                        (center[0] + big_cross_length/2.0, center[1]+big_cross_width/2.0),
                        (center[0] + big_cross_length/2.0, center[1]-big_cross_width/2.0)]   
        cross_horizontal_r = core.Boundary(cross_horizontal_p_r, layer=self.layer_main)
        self.cell.add(cross_horizontal_r)
        
        cross_vertical_p_u = [(center[0] - big_cross_width/2.0, center[1]+big_cross_width),
                        (center[0] - big_cross_width/2.0, center[1]+big_cross_length/2.0),
                        (center[0] + big_cross_width/2.0, center[1]+big_cross_length/2.0),
                        (center[0] + big_cross_width/2.0, center[1]+big_cross_width)]   
        cross_vertical_u = core.Boundary(cross_vertical_p_u, layer=self.layer_main)
        self.cell.add(cross_vertical_u)
        
        cross_vertical_p_l = [(center[0] - big_cross_width/2.0, center[1]-big_cross_length/2.0),
                        (center[0] - big_cross_width/2.0, center[1]-big_cross_width),
                        (center[0] + big_cross_width/2.0, center[1]-big_cross_width),
                        (center[0] + big_cross_width/2.0, center[1]-big_cross_length/2.0)]   
        cross_vertical_l = core.Boundary(cross_vertical_p_l, layer=self.layer_main)
        self.cell.add(cross_vertical_l)
        
        lc_hor = shapes.Rectangle((center[0]-big_cross_width/2.0, center[1] - little_cross_width/2.0), (center[0]+big_cross_width/2.0, center[1] + little_cross_width/2.0), layer=self.layer_main)
        lc_ver = shapes.Rectangle((center[0]-little_cross_width/2.0, center[1] - big_cross_width/2.0), (center[0]+little_cross_width/2.0, center[1] + big_cross_width/2.0), layer=self.layer_main)
        self.cell.add(lc_hor)
        self.cell.add(lc_ver)
        
    
if __name__ == "__main__":
    am = AlignmentMarker("am")
    am.cell.show()