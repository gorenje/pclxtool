import types, math, sys, re

from .point import *
from .geombase import geombase

__all__ = [ "Circle" ]

class Circle( geombase ):

    # constructor method
    def __init__(self, center, radius):
        self.__radius = radius
        self.__cpt = center.clone()
        geombase.__init__(self)

    # representation method for debugging, return string
    def __repr__(self):
        return "Circle( %s, %f )" % (repr(self.getCenter()), self.getRadius())

    # string method returns an informal representation of the object
    def __str__(self):
        return "Circle: Center: %s Radius: %f" \
               % (repr(self.getCenter()), self.getRadius())

    def getCenter(self):
        return self.__cpt.clone()

    def getRadius(self):
        return self.__radius

    # scale the circle
    def __mul__(self, val):
        return Circle( self.getCenter() * val, self.getRadius() * val )

    # translate the circle, moving it's center point
    def __sub__(self, pt):
        return Circle( self.getCenter() - pt, self.getRadius() )

    def length( self, time_step = 0.01 ):
        return ( 2 * math.pi * self.getRadius() )

    def clone(self):
        return Circle( self.getCenter().clone(), self.getRadius() )

    def get_points( self, point_count = 10 ):
        pts = []
        delta = (2 * math.pi) / float(point_count)
        radius = self.getRadius()
        cpt = self.getCenter()

        for idx in range( point_count ):
            pts.append( Point( radius * math.cos( delta * idx ) + cpt.x,
                               radius * math.sin( delta * idx ) + cpt.y ))

        return self._handleReverseStartPoint( pts )
