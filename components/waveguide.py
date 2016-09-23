# -*- coding: utf-8 -*-
"""
Created on Fri Jul 01 13:53:57 2016

@author: dkita
"""

from gdsCAD import *
from wrapped_disk import WrappedDisk
import os
print(os.getcwd())


class WaveguideTemplate:
    def __init__(self, bend_radius=50.0, wg_width=2.0, clad_width=15.0, wg_layer=1, clad_layer=2):
        self.wg_width = wg_width
        self.bend_radius = bend_radius
        self.clad_width = clad_width
        self.wg_layer = wg_layer
        self.clad_layer = clad_layer

class Waveguide:
    def __init__(self, name, trace, waveguide_template):
        self.cell = core.Cell(str(name))
        self.trace = trace
        self.components = []
        
        self.wg_t = waveguide_template
        
        self.wg_layer = waveguide_template.wg_layer
        self.clad_layer = waveguide_template.clad_layer
        
        self.build_cell()
        
    def sign(self, number):
        if number > 0:
            return 1
        if number < 0:
            return -1
        if number==0:
            return 0
            
    def getComponents(self): return self.components
        
    def build_cell(self):
        """ Route the waveguide along the specified trace path  """
        
        """ First, start with a square trace between the two points  """
        br = self.wg_t.bend_radius
        wg_width = self.wg_t.wg_width
        clad_width = self.wg_t.clad_width
        
        for i in xrange(len(self.trace)-2):
            p0 = self.trace[i]
            p1 = self.trace[i+1] #This is the corner piece
            p2 = self.trace[i+2]
            """ Construct waveguide corners """
            center = [p1[0] - self.sign(p1[0]-p0[0])*br - self.sign(p1[0]-p2[0])*br,
                      p1[1] - self.sign(p1[1]-p0[1])*br - self.sign(p1[1]-p2[1])*br]
            
            if center[0] > p1[0] and center[1] > p1[1]:
                ia = 270
                fa = 180
            if center[0] < p1[0] and center[1] > p1[1]:
                ia = 0
                fa = -90
            if center[0] > p1[0] and center[1] < p1[1]:
                ia = 180
                fa = 90
            if center[0] < p1[0] and center[1] < p1[1]:
                ia = 90
                fa = 0
            
            wg_arc = shapes.Disk(center, br+wg_width/2.0, inner_radius = br-wg_width/2.0,
                                 initial_angle = ia, final_angle = fa, layer=self.wg_layer)
            cld_arc = shapes.Disk(center, br+clad_width/2.0, inner_radius = br-clad_width/2.0,
                                 initial_angle = ia, final_angle = fa, layer=self.clad_layer)
            self.components.append(cld_arc)
            self.components.append(wg_arc)
            
            """ Now route straight wg sections """
            if i!=0:
                if p0[0]==p1[0]:
                    """ Vertical waveguide """
                    s = self.sign(p0[1]-p1[1])
                    wg = shapes.Rectangle((p0[0]-wg_width/2.0, p0[1]-s*br), (p1[0]+wg_width/2.0, p1[1]+s*br), layer=self.wg_layer)
                    cld = shapes.Rectangle((p0[0]-clad_width/2.0, p0[1]-s*br), (p1[0]+clad_width/2.0, p1[1]+s*br), layer=self.clad_layer)                    
                    self.components.append(cld)
                    self.components.append(wg)                    
                elif p0[1]==p1[1]:
                    """ Horizontal waveguide """
                    s = self.sign(p0[0]-p1[0])
                    wg = shapes.Rectangle((p0[0]-s*br, p0[1]-wg_width/2.0), (p1[0]+s*br, p1[1]+wg_width/2.0), layer=self.wg_layer)
                    cld = shapes.Rectangle((p0[0]-s*br, p0[1]-clad_width/2.0), (p1[0]+s*br, p1[1]+clad_width/2.0), layer=self.clad_layer)
                    self.components.append(cld)
                    self.components.append(wg) 
        
        if len(self.trace)==2:
            """ There are no waveguide bends, so straight sections are treated
            a little differently (routed directly to trace endpoints)"""
            p0 = self.trace[0]
            p1 = self.trace[1]
            if p0[0]==p1[0]:
                """ Vertical waveguide """
                s = self.sign(p0[1]-p1[1])
                wg = shapes.Rectangle((p0[0]-wg_width/2.0, p0[1]), (p1[0]+wg_width/2.0, p1[1]), layer=self.wg_layer)
                cld = shapes.Rectangle((p0[0]-clad_width/2.0, p0[1]), (p1[0]+clad_width/2.0, p1[1]), layer=self.clad_layer)
                self.components.append(cld)
                self.components.append(wg) 
            elif p0[1]==p1[1]:
                """ Horizontal waveguide """
                s = self.sign(p0[0]-p1[0])
                wg = shapes.Rectangle((p0[0], p0[1]-wg_width/2.0), (p1[0], p1[1]+wg_width/2.0), layer=self.wg_layer)
                cld = shapes.Rectangle((p0[0], p0[1]-clad_width/2.0), (p1[0], p1[1]+clad_width/2.0), layer=self.clad_layer)
                self.components.append(cld)
                self.components.append(wg) 
        else:
            """ Now route the straight wg sections from bends to ports """
            p0 = self.trace[0]
            p1 = self.trace[1]
            if p0[0]==p1[0]:
                """ Vertical waveguide """
                print "vertical wg"
                s = self.sign(p0[1]-p1[1])
                wg = shapes.Rectangle((p0[0]-wg_width/2.0, p0[1]), (p1[0]+wg_width/2.0, p1[1]+s*br), layer=self.wg_layer)
                cld = shapes.Rectangle((p0[0]-clad_width/2.0, p0[1]), (p1[0]+clad_width/2.0, p1[1]+s*br), layer=self.clad_layer)
                self.components.append(cld)
                self.components.append(wg) 
            elif p0[1]==p1[1]:
                """ Horizontal waveguide """
                print "horizontal wg"
                print p0, p1
                s = self.sign(p0[0]-p1[0])
                wg = shapes.Rectangle((p0[0], p0[1]-wg_width/2.0), (p1[0]+s*br, p1[1]+wg_width/2.0), layer=self.wg_layer)
                cld = shapes.Rectangle((p0[0], p0[1]-clad_width/2.0), (p1[0]+s*br, p1[1]+clad_width/2.0), layer=self.clad_layer)
                print wg
                self.components.append(cld)
                self.components.append(wg) 
                
            p0 = self.trace[-1]
            p1 = self.trace[-2]
            if p0[0]==p1[0]:
                """ Vertical waveguide """
                s = self.sign(p0[1]-p1[1])
                wg = shapes.Rectangle((p0[0]-wg_width/2.0, p0[1]), (p1[0]+wg_width/2.0, p1[1]+s*br), layer=self.wg_layer)
                cld = shapes.Rectangle((p0[0]-clad_width/2.0, p0[1]), (p1[0]+clad_width/2.0, p1[1]+s*br), layer=self.clad_layer)
                self.components.append(cld)
                self.components.append(wg) 
            elif p0[1]==p1[1]:
                """ Horizontal waveguide """
                s = self.sign(p0[0]-p1[0])
                wg = shapes.Rectangle((p0[0], p0[1]-wg_width/2.0), (p1[0]+s*br, p1[1]+wg_width/2.0), layer=self.wg_layer)
                cld = shapes.Rectangle((p0[0], p0[1]-clad_width/2.0), (p1[0]+s*br, p1[1]+clad_width/2.0), layer=self.clad_layer)
                self.components.append(cld)
                self.components.append(wg) 
        
    
if __name__ == "__main__":
    top = core.Cell('Top')
    wd1 = WrappedDisk("d1", (-300,-100))
    wd2 = WrappedDisk("d2", (300,100))
    top.add(wd1.cell)
    top.add(wd2.cell)
    
    wg = Waveguide('wg', wd1.portlist["right"], wd2.portlist["left"])
    top.add(wg.cell)
    
    top.show()