""" Utility functions and classes for SRP

Context : SRP
Module  : Math.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 05/09/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (05/09/2010) First version.

"""

import math

from AstroAngleInput import AstroAngleInput


class Point:
    def __init__ (self, coord):
        self.Coord = coord
        
    def PointDist (self, other):
        dist = math.sqrt((self.Coord[0]-other.Coord[0])**2 + (self.Coord[1]-other.Coord[1])**2)
        return dist
        
    def AngOrig (self,orig=(0.0,0.0)):
        xcoord = self.Coord[0] - orig[0]
        ycoord = self.Coord[1] - orig[1]
        if ycoord <= xcoord:
            ang = math.degrees(math.atan2(ycoord,xcoord))
        else:
            ang = math.degrees(math.atan2(xcoord,ycoord))
            ang = 90.0 - ang
        return ang
        
    def __str__(self):
        return "%g %g" % (self.Coord[0], self.Coord[1])