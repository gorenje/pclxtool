"""
This is an "interface" for geometry shapes to implement in order to be used
with in the flash-tools environment.

__mul__(scale): implements the multiple operator and should scale the shape by
the factor given.

__sub__(point): implements a translation of the shape by the given point. It
actually represents the subtract operator.

XXXXX more description XXXXX
"""

import types, math, sys, re

__all__ = [ "geombase" ]

class geombase:

    # insert any class variables here

    # constructor method
    def __init__(self):
        self.start_point = None
        self.reverse_order = False

    def __mul__(self, scale):
        raise NotImplementedError

    def __sub__( self, pt ):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def clone( self ):
        raise NotImplementedError

    def get_points( self, point_count = 10 ):
        raise NotImplementedError

    # calling reverse without an argument causes the existing value to be
    # toggled.
    def reverse(self, val = None):
        if val == None:  self.reverse_order = not self.reverse_order
        else:            self.reverse_order = val

    def length(self, time_step = 0.01 ):
        plist = self.get_points( int(1.0 / float(time_step)) )
        length = 0
        last_pt = plist[0]
        for pt in plist[1:]:
            length += last_pt.distance( pt )
            last_pt = pt
        return length

    # Note: using startings points should only be used for "closed" shapes,
    # (i.e. circles, rectangles, ellipses) where the points are continues.
    # Using start points with lines causes a "jump".
    def setStartPoint( self, pt = None):
        if pt == None: self.start_point = None
        else:          self.start_point = pt.clone()

    def _handleReverseStartPoint( self, plist ):
        if self.reverse_order == True:
            plist.reverse()

        if not self.start_point == None:
            lens = map( lambda pt: self.start_point.distance( pt ), plist )
            min_idx = lens.index(min(lens))
            plist = plist[min_idx:] + plist[:min_idx]

        return plist
