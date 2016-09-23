# -*- coding: utf-8 -*-
"""
Created on Sun Jul 03 13:36:51 2016

@author: dkita
"""
from gdsCAD import *
import numpy as np
import math
import heapq
from waveguide import Waveguide, WaveguideTemplate
    
class Cell:
    """
    Cell class for PDK toolkit that manages the cell classes created in 
    gdsCAD, making it easier to manipulate for photonics applications 
    (waveguide routing, management, etc.) 
    
    Syntax is identical to gdsCAD cells, but has more functionality
    """
    def __init__(self, name):
        self.gdscell = core.Cell(name)
        self.components = {}
        
    def add(self, component):
        self.gdscell.add(component.cell)
        self.components[component.cell.name] = component
    
    def add_individual(self, component):
        self.gdscell.add(component)
        
def rotate(component, angle):
    center = component.center
    comp_copy = component.cell.copy()
    """ Delete old cell contents """
    name = component.cell.name
    component.cell = core.Cell(name)
    
    layer_list = comp_copy.get_layers()
    layer_list.reverse()  # for aesthetics
    for layer in layer_list:
        subcell = core.Cell("temp_subcell"+str(layer))
        for elem in comp_copy.elements:
            if elem.layer == layer:
                subcell.add(elem)
        
        comp_elems = core.Elements(subcell, layer=layer)
        comp_elems.translate((-center[0], -center[1]))
        comp_elems.rotate(angle)
        comp_elems.translate((center[0], center[1]))
        component.cell.add(comp_elems)
    
    for name in component.portlist:
        loc = component.portlist[name]
        
        """ Create vectors & rotation matrix """
        v=np.array([[loc[0]-center[0]], [loc[1]-center[1]]])
        theta = np.radians(angle)
        c, s = np.cos(theta), np.sin(theta)
        R = np.matrix('{} {}; {} {}'.format(c, -s, s, c))
        vn = R*v

        component.portlist[name][0]=float(vn[0])+center[0]
        component.portlist[name][1]=float(vn[1])+center[1]
        if 45<(angle%360)<135:
            component.portlist[name][2] = flipDirectionCCW(component.portlist[name][2])
        if 135<(angle%360)<225:
            component.portlist[name][2] = flipDirection(component.portlist[name][2])
        if 225<(angle%360)<315:
            component.portlist[name][2] = flipDirectionCW(component.portlist[name][2])
        
    return component
    
#def translate(component, vector):
#    """ translate component by amount vector [x, y] """
#    center = component.center
#    comp_copy = component.cell.copy()
#    """ Delete old cell contents """
#    name = component.cell.name
#    component.cell = core.Cell(name)
#    
#    layer_list = comp_copy.get_layers()
#    layer_list.reverse()  # for aesthetics
#    
#    for layer in layer_list:
#        subcell = core.Cell("temp_subcell"+str(layer))
#        for elem in comp_copy.elements:
#            if elem.layer == layer:
#                subcell.add(elem)
#        
#        comp_elems = core.Elements(subcell, layer=layer)
#        comp_elems.translate((-center[0], -center[1]))
#        comp_elems.rotate(angle)
#        comp_elems.translate((center[0], center[1]))
#        component.cell.add(comp_elems)
#    
#    return component
        
def flipDirection(direction):
    if direction=="NORTH": return "SOUTH"
    if direction=="WEST": return "EAST"
    if direction=="SOUTH": return "NORTH"
    if direction=="EAST": return "WEST"
    
def flipDirectionCW(direction):
    if direction=="NORTH": return "EAST"
    if direction=="WEST": return "NORTH"
    if direction=="SOUTH": return "WEST"
    if direction=="EAST": return "SOUTH"
    
def flipDirectionCCW(direction):
    if direction=="NORTH": return "WEST"
    if direction=="WEST": return "SOUTH"
    if direction=="SOUTH": return "EAST"
    if direction=="EAST": return "NORTH"

def autoBuildWaveguides(top, netlist, waveguide_template):
    for net in netlist:
        trace = autoroute(top, net, waveguide_template)
        print trace
        wg = Waveguide("wg0", trace, waveguide_template)
        for component in wg.getComponents():
            top.add_individual(component)
            
def buildWaveguides(top, tracelist, waveguide_template):
    for trace in tracelist:
        wg = Waveguide("wg0", trace, waveguide_template)
        for component in wg.getComponents():
            top.add_individual(component)
            
def buildWaveguidesInSubclass(top, tracelist, waveguide_template):
    for trace in tracelist:
        wg = Waveguide("wg0", trace, waveguide_template)
        for component in wg.getComponents():
            top.add(component)
            
def bounding_boxes(topcell):
    cell_bbs = []
    for cell in topcell.gdscell.elements:
        cell_bbs.append(cell.bounding_box)
    return cell_bbs
    
def enlarge(bb, length):
    """ Add 'length' to each side of a bounding box 'bb' """
    bb_new = []
    bb_new.append([bb[0][0]-length, bb[0][1]-length])
    bb_new.append([bb[1][0]+length, bb[1][1]+length])

    return np.array(bb_new)

def moveNetlists(netlist, dist):
    ports = []
    for j in xrange(2):
        if netlist[j][2]=="NORTH":
            ports.append([netlist[j][0], netlist[j][1]+dist, netlist[j][2]])
        if netlist[j][2]=="WEST":
            ports.append([netlist[j][0]-dist, netlist[j][1], netlist[j][2]])
        if netlist[j][2]=="SOUTH":
            ports.append([netlist[j][0], netlist[j][1]-dist, netlist[j][2]])
        if netlist[j][2]=="EAST":
            ports.append([netlist[j][0]+dist, netlist[j][1], netlist[j][2]])
    return (ports[0], ports[1])
    
def isInside(point, bb):
    if ((point[0] >= bb[0][0]) and (point[0] < bb[1][0]) and (point[1] >= bb[0][1]) and (point[1] < bb[1][1])):
        return True
    else:
        return False
        
def doBoxesIntersect(b1, b2):
    """Input: two boundary boxes"""
    b1x_c = (b1[0][0]+b1[1][0])/2.0
    b1y_c = (b1[0][1]+b1[1][1])/2.0
    width1 = abs(b1[1][0]-b1[0][0])
    height1 = abs(b1[1][1]-b1[0][1])    
    
    b2x_c = (b2[0][0]+b2[1][0])/2.0
    b2y_c = (b2[0][1]+b2[1][1])/2.0
    width2 = abs(b2[1][0]-b2[0][0])
    height2 = abs(b2[1][1]-b2[0][1])  
    
    canTouchX = (2*abs(b1x_c - b2x_c) < (width1 + width2))
    canTouchY = (2*abs(b1y_c - b2y_c) < (height1 + height2))
    
    return (canTouchX and canTouchY)
    
        
def getBBpoints(bb):
    return [[bb[0][0], bb[0][1]],
            [bb[0][0], bb[1][1]],
            [bb[1][0], bb[0][1]],
            [bb[1][0], bb[1][1]]]

def checkBBoverlaps(bbs):
    """ Check to make sure none of the cells are overlapping """
    for i in xrange(len(bbs)):
        bb = bbs[i]
        other_bbs = [x for j,x in enumerate(bbs) if j!=i]
        for obb in other_bbs:
            return doBoxesIntersect(obb, bb)
        
    return False
    
def visualize_grid(grid, meshsize, xmin, ymin):
    grid = grid[::-1]
    import matplotlib.pyplot as plt
    import matplotlib
    fig, ax = plt.subplots(1, 1, tight_layout=True)
    my_cmap = matplotlib.colors.ListedColormap(['w', 'b', 'r', 'g', 'y'])
    Nx, Ny = len(grid[0]), len(grid)
    for y in xrange(Ny+1):
        ax.axhline(ymin + y*meshsize, lw=2, color='k', zorder=5)
    for x in xrange(Nx+1):
        ax.axvline(xmin + x*meshsize, lw=2, color='k', zorder=5)
    
    print "plotting..."
    print [xmin, xmin + Nx*meshsize, ymin, ymin + Ny*meshsize]
    ax.imshow(np.array(grid), interpolation='none', cmap=my_cmap, extent=[xmin, xmin + Nx*meshsize, ymin, ymin + Ny*meshsize], zorder=0)
    plt.show()
    
    
def autogrid(layoutBB, cell_bbs, netlist, meshsize):
    """ Each grid point represents the LOWER RIGHT corner of the grid box """
    xmin, xmax, ymin, ymax = layoutBB[0][0], layoutBB[1][0], layoutBB[0][1], layoutBB[1][1]
    xlist = np.arange(xmin, xmax+meshsize, meshsize)
    ylist = np.arange(ymin, ymax+meshsize, meshsize)
    grid = []
    """ Make a copy of netlist that isn't a tuple """
    netlist_grid = [None, None]
    
        
    for j in xrange(len(ylist)-1):
        row = []
        for i in xrange(len(xlist)-1):
#            corners = [[xlist[i], ylist[j]], 
#                       [xlist[i]+meshsize, ylist[j]], 
#                       [xlist[i], ylist[j]+meshsize], 
#                       [xlist[i]+meshsize, ylist[j]+meshsize]]
            cornerBB = [[xlist[i], ylist[j]], [xlist[i]+meshsize, ylist[j]+meshsize]]
            
            occupied = 0 #not occupied
            for bb in cell_bbs:
                if doBoxesIntersect(bb, cornerBB):
                    occupied=1
            
            if isInside(netlist[0], cornerBB):
                netlist_grid[0] = [i, j]
                occupied = 2
            if isInside(netlist[1], cornerBB):
                netlist_grid[1] = [i, j]                    
                occupied = 2
            
            row.append(occupied)
            
        grid.append(row)
    return grid, netlist_grid
    
def getWaypoints(corners, netlist_pair, layoutBB, meshsize):
    """ Each grid point represents the LOWER RIGHT corner of the grid box """
    xmin, xmax, ymin, ymax = layoutBB[0][0], layoutBB[1][0], layoutBB[0][1], layoutBB[1][1]
    xlist = np.arange(xmin, xmax+meshsize, meshsize)
    ylist = np.arange(ymin, ymax+meshsize, meshsize)
    
    new_corners = [[netlist_pair[0][0], netlist_pair[0][1]]]    
    for corner in corners:
        new_corners.append([xlist[corner[0]]+meshsize/2.0, ylist[corner[1]]+meshsize/2.0])
    new_corners.append([netlist_pair[1][0], netlist_pair[1][1]])
    
    """Make corrections to ensure straight lines between ports and corners """
    if netlist_pair[0][2]=="EAST" or netlist_pair[0][2]=="WEST":
        new_corners[1][1] = new_corners[0][1]
    if netlist_pair[0][2]=="NORTH" or netlist_pair[0][2]=="SOUTH":
        new_corners[1][0] = new_corners[0][0]
        
    if netlist_pair[-1][2]=="EAST" or netlist_pair[-1][2]=="WEST":
        new_corners[-2][1] = new_corners[-1][1]
    if netlist_pair[-1][2]=="NORTH" or netlist_pair[-1][2]=="SOUTH":
        new_corners[-2][0] = new_corners[-1][0]
        
    return new_corners
    
def findCorners(path, netlist_pair):
    corners = []
    for i in xrange(len(path)):
        """ First search for normal corners, not on first/last points """
        if i!=0 and i!=(len(path)-1):
            xsame = (path[i][0]==path[i+1][0]==path[i-1][0])
            ysame = (path[i][1]==path[i+1][1]==path[i-1][1])
            if not xsame and not ysame:
                corners.append(path[i])
        
        else:
            """ Now, look to see if first/last points are corners """
            """ MAY NOT NEED THIS CODE ANYMORE """
            if i==0:
                if netlist_pair[0][2]=="EAST" or netlist_pair[0][2]=="WEST":
                    ysame = (path[i][1]==path[i+1][1]) 
                    if not ysame:
                        corners.append(path[i])
                elif netlist_pair[0][2]=="NORTH" or netlist_pair[0][2]=="SOUTH":
                    xsame = (path[i][0]==path[i+1][0])
                    if not xsame:
                        corners.append(path[i])
            
            elif i==(len(path)-1):
                if netlist_pair[1][2]=="EAST" or netlist_pair[1][2]=="WEST":
                    ysame = (path[i][1]==path[i-1][1]) 
                    if not ysame:
                        corners.append(path[i])
                elif netlist_pair[1][2]=="NORTH" or netlist_pair[1][2]=="SOUTH":
                    xsame = (path[i][0]==path[i-1][0])
                    if not xsame:
                        corners.append(path[i])
    return corners

def autoroute(topcell, netlist, wg_t, meshsize=None, check_overlaps=False):
    if meshsize==None:
        """ This default ensures that two corners can't be routed too close
        to one another """
        meshsize=1.0*wg_t.bend_radius
    
    """ Make the BBs larger to avoid waveguides getting too close """
    cell_bbs = bounding_boxes(topcell)
#    for i in xrange(len(cell_bbs)):
#        cell_bbs[i] = enlarge(cell_bbs[i], wg_t.clad_width)
    """ Enlarge layout BB to allow routing of waveguides around components """
    layout_BB = enlarge(topcell.gdscell.bounding_box, wg_t.clad_width + 5*wg_t.bend_radius)
    
    """ Make sure netlists are accessible from enlarged component BBs """
    netlist_routing = moveNetlists(netlist, wg_t.bend_radius)
    
    """ By default, OFF.  User is responsible for preventing placement of 
    overlapping components """
    if check_overlaps:
        if checkBBoverlaps(cell_bbs):
            raise Exception('At least one cell in the design is overlapping with another cell, or too close for waveguide autorouting')

    """ Convert the net and list of BBs into a square grid that we can route on """
    grid, netlist_grid = autogrid(layout_BB, cell_bbs, netlist_routing, meshsize)

    """ Uncomment below to visualize the grid generated """
    """ White = free tile, blue = tile occupied by BB, red = port """
    xmin, ymin = layout_BB[0][0], layout_BB[1][0]
#    visualize_grid(grid, meshsize, xmin, ymin)
    
    """ Effective bend_radius in units of 'mesh squares' """
    br = 1+int(1.5*wg_t.bend_radius/meshsize)
    graph = SquareGrid(grid, br)
    start = (netlist_grid[0][0], netlist_grid[0][1], netlist[0][2])
    end = (netlist_grid[1][0], netlist_grid[1][1], flipDirection(netlist[1][2]))
    """ Implement A* search algorithm """
    came_from, cost_so_far = a_star_search(graph, start, end, xmin, ymin, meshsize, grid)
    path =  reconstruct_path(came_from, start, end)

    corners = findCorners(fix_path(path), netlist)

    """ Take the grid path and return entire list of waypoints for the waveguide """
    return getWaypoints(corners, netlist, layout_BB, meshsize)

"""
Below is the A-star routing algorithm
"""
        
class PriorityQueue:
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]

class SquareGrid:
    def __init__(self, graph, bend_radius):
        self.graph = graph        
        self.br = bend_radius
    
    def in_bounds(self, id):
        (x, y, direction) = id
        return 0 <= x < len(self.graph[0]) and 0 <= y < len(self.graph)
        
    def passable(self, id):
        (x, y, direction) = id
        return self.graph[y][x]!=1
            
    def neighbors(self, id, prev_node):
        (x, y, direction) = id
        """ Show either only the square in front, or the squares after making
        a turn left or right """
        if direction=="NORTH":
            results = [(x,y+1, direction), (x-self.br, y+self.br, "WEST"), (x+self.br, y+self.br, "EAST")]
        if direction=="SOUTH":
            results = [(x,y-1, direction), (x-self.br, y-self.br, "WEST"), (x+self.br, y-self.br, "EAST")]
        if direction=="WEST":
            results = [(x-1,y, direction), (x-self.br, y+self.br, "NORTH"), (x-self.br, y-self.br, "SOUTH")]
        if direction=="EAST":
            results = [(x+1,y, direction), (x+self.br, y+self.br, "NORTH"), (x+self.br, y-self.br, "SOUTH")]
        
        results = filter(self.in_bounds, results)
        results = filter(self.passable, results)
        return results
        
    def cost(self, prev_node, cur_node, next_node):
        (x, y, d) = cur_node
        if prev_node == None: ## First step, can only go straight
            return 1

        (xn, yn, d) = next_node
        
        if (xn==x) or (yn==y):
            """ Check if the next step is straight ahead """
            return 1
            
        elif ((xn-x)!=0) and ((yn-y)!=0):
            """ Check if the next step is a bend """
            penalty = 10.0
            return 2*self.br + penalty
        else:
            print "WARNING:  No routing cost was able to be determined in A* algorithm for cur_node: "+str(cur_node)+", prev_node: "+str(prev_node)+", and next_node: "+str(next_node)
            return None
         
def heuristic(a, b):
    (x1, y1, d) = a
    (x2, y2, d) = b
    return abs(x1 - x2) + abs(y1 - y2)
    
def a_star_search(graph, start, goal, xmin, ymin, meshsize, grid):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while not frontier.empty():
        current = frontier.get()
        if current == goal:
            print "Found goal at "+str(current)+" with cost "+str(cost_so_far[current])
            break
        
        for next in graph.neighbors(current, came_from[current]):
            new_cost = cost_so_far[current] + graph.cost(came_from[current], current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put(next, priority)
                came_from[next] = current
                
                """ Uncomment below to view algorithm in progress """
#                curvalue = grid[current[1]][current[0]]
#                nexvalue = grid[next[1]][next[0]]
#                grid[current[1]][current[0]]=3
#                grid[next[1]][next[0]] = 4
#                visualize_grid(grid, meshsize, xmin, ymin)
#                grid[current[1]][current[0]] = curvalue #return to original state
#                grid[next[1]][next[0]]=nexvalue
  

    if frontier.empty():
        raise Exception("No waveguide route was able to be found.")
    
    return came_from, cost_so_far
    
def reconstruct_path(came_from, start, goal):
    current = goal
    path = [current]
    while current != start:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path
    
def fix_path(path):
    newpath = [(path[0][0], path[0][1])]
    for i in xrange(len(path)-1):
        (x1, y1, d1) = path[i]
        (x2, y2, d2) = path[i+1]
#        newpath.append((path[i][0], path[i][1]))
        if (d1!=d2):
            """ Bend detected, add an extra point """
            if d1=="NORTH" or d1=="SOUTH":
                newpath.append((x1, y2))
            if d1=="WEST" or d1=="EAST":
                newpath.append((x2, y1))
        newpath.append((path[i+1][0], path[i+1][1]))
    return newpath