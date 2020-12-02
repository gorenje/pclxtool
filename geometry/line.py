import types, math, sys, re

from .point import *
from .geombase import geombase

# __all__ defines what should be accessible outside of this file
__all__ = [ "Line" ]

###### Line class
class Line(geombase):

    def __init__(self, pt1, pt2):
        self.yinsect = None
        self.slope = None
        self.c = None
        self.points = []
        assert_is_point( pt1 )
        assert_is_point( pt2 )
        self.points = [ pt1, pt2 ]
        try:
            self.slope = float(pt1.slope(pt2))
            self.yinsect = float(pt1.y) - float(self.slope * pt1.x)
        except PointsVerticalError:
            self.c = pt1.x
        except SamePointsError:
            print("## Same Points Error - slope and yinsect undefined")
            print("## Point1: " + str(pt1) + " Point2: " + str(pt2))
#            raise SamePointsError( "points passed to line are the same" )
        geombase.__init__(self)

    def get_point_1(self):
        return self.points[0].clone()

    def get_point_2(self):
        return self.points[1].clone()

    def clone(self):
        return Line( self.get_point_1(), self.get_point_2() )

    # return true if this line is vertical
    def is_vertical(self):
        return ( self.c != None )
    def get_c(self):
        return self.c

    # returns true if the two lines are parallel
    def are_parallel(self, lne):
        assert_is_line( lne )
        return ( (self.is_vertical() and lne.is_vertical())
                 or self.slope == lne.slope );

    # string representation for a line
    def __str__(self):
        if self.is_vertical():
            return "Line is vertical: y = " + str(self.c)
        else:
            return "Line: y = " + str(self.slope) + "*x + " + str(self.yinsect)

    def __repr__(self):
        return "Line( %s, %s )" % (repr(self.points[0]), repr(self.points[1]))

    def __mul__(self, val):
        return Line( self.points[0] * val, self.points[1] * val )

    def __sub__(self, pt):
        return Line( self.points[0] - pt, self.points[1] - pt )

    # return the point where these two lines intersect
    def intersection( self, lne ):
        assert_is_line( lne )
        if self.is_parallel( lne ):
            raise LinesAreParallelError
        if self.is_vertical():
            return Point( self.c, (lne.slope * self.c) + lne.yinsect )
        if lne.is_vertical():
            return Point( lne.c, (self.slope * lne.c) + self.yinsect );
        xval = (lne.yinsect-self.yinsect) / (self.slope-lne.slope);
        return Point( xval, (self.slope * xval) + self.yinsect )

    # returns true if the point is on the line.
    # this uses the repr(...) function to convert the floating point numbers
    # to strings and then the string representations are compared. This might
    # cause unexpected results.
    def on_line( self, pt ):
        assert_is_point( pt )
        if self.is_vertical():
            return (repr(pt.x) == repr(self.c))
        else:
            return (repr(pt.y) == repr(((self.slope * pt.x) + self.yinsect)))

    # return point_count points equally spaced out along this line beginning
    # at pt1 (as given in the constructor) and ending with pt2.
    def get_points( self, point_count = 10 ):
        res = []
        if point_count <= 1:
            res.append( self.points[0] )
        else:
            for idx in range( point_count ):
                res.append( self.points[0]
                            .point_on_segment( self.points[1],
                                               float(idx)/
                                               float(point_count-1)))
        return self._handleReverseStartPoint( res )

    # length of this line is defined as being the distance between the
    # two points used to define this line. The time_step argument is defined
    # for completeness (bezier and ellipse also allow time_step): it is
    # ignored.
    def length( self, time_step = 0.01 ):
        return self.points[0].distance( self.points[1] )

if __name__ == '__main__':
    p = Point( 1, 3 )
    assert(  repr(p.v_length()) == repr(3.1622776601683795))
    p2 = Point( 23, 23)
    assert( repr(p.v_angle( p2 )) == repr( 0.46364760900080643 ) )
    assert( repr(p.slope( p2 )) == repr(0.90909090909090906 ))
    assert( repr(p2.slope( p )) == repr(0.90909090909090906 ))
    assert( str(Line( p, p2 )) == "Line: y = 0.909090909091*x + 2.09090909091")
    p = Point( 1, 1 )
    p2 = p

    assert( p == p2 )

    try:
        print(Line( p, p2 ))
        assert( False )
    except SamePointsError:
        pass

    p = Point( 0, 0 )
    p2 = Point( 10, 10 )
    assert( p.midpoint( p2 ) == Point( 5, 5 ) )
    assert( p.distance( p2.midpoint( p ) ) == p.distance( p.midpoint( p2 ) ))
    assert( p2.distance( p2.midpoint( p ) ) == p.distance( p.midpoint( p2 ) ))
    assert( p.distance( p2 ) > 13 and p.distance( p2 ) < 15 )
    assert( p.distance( p2 ) == p2.distance( p ) )

    p = Point( 23, -32 )
    p2 = Point( -64, 64 )
    assert( p.midpoint( p2 ) == Point( -20.5, 16.0 ) )
    assert( p.distance( p2.midpoint( p ) ) == p.distance( p.midpoint( p2 ) ))
    assert( p2.distance( p2.midpoint( p ) ) == p.distance( p.midpoint( p2 ) ))
    assert( p.distance( p2 ) > 128 and p.distance( p2 ) < 130 )
    assert( p.distance( p2 ) == p2.distance( p ) )

    p = Point( -33, -12 )
    p2 = Point( 33, 12 )
    assert( p.midpoint( p2 ) == Point( 0,0 ) )
    assert( p.distance( p2.midpoint( p ) ) == p.distance( p.midpoint( p2 ) ))
    assert( p2.distance( p2.midpoint( p ) ) == p.distance( p.midpoint( p2 ) ))
    assert( p.distance( p2 ) > 70 and p.distance( p2 ) < 71 )
    assert( p.distance( p2 ) == p2.distance( p ) )

    p = Point( -33, -12 )
    p2 = Point( -34, -13 )
    assert( p.midpoint( p2 ) == Point( -33.5, -12.5 ) )
    assert( p.distance( p2.midpoint( p ) ) == p.distance( p.midpoint( p2 ) ))
    assert( p2.distance( p2.midpoint( p ) ) == p.distance( p.midpoint( p2 ) ))
    assert( p.distance( p2 ) > 1 and p.distance( p2 ) < 2 )
    assert( p.distance( p2 ) == p2.distance( p ) )

    p = Point( 23, -17 )
    p2 = Point( 23, -17 )
    assert( p.midpoint( p2 ) == Point( 23, -17 ) )
    assert( p.distance( p2.midpoint( p ) ) == p.distance( p.midpoint( p2 ) ))
    assert( p2.distance( p2.midpoint( p ) ) == p.distance( p.midpoint( p2 ) ))
    assert( p.distance( p2 ) > -1 and p.distance( p2 ) < 1 )
    assert( p.distance( p2 ) == p2.distance( p ) )

    p = Point( 10, 10 )
    p2 = Point( 0, 0 )
    l = Line( p, p2 )
    assert( l.on_line( Point( 5, 5 ) ) )
    assert( l.on_line( Point( 5, 6 ) ) == False )
    assert( l.on_line( Point( 5, 4 ) ) == False )

    p = Point( 10, 10 )
    p2 = Point( 10, 0 )
    l = Line( p, p2 )
    assert( l.on_line( Point( 10, 5 ) ) )
    assert( l.on_line( Point( 10, -1 ) ) )
    assert( l.on_line( Point( 10, 1 ) ) )
    assert( l.on_line( Point( 10, 2 ) ) )
    assert( l.on_line( Point( 5, 6 ) ) == False )
    assert( l.on_line( Point( 5, 4 ) ) == False )

    assert( len( l.get_points( 10 ) ) == 10 )
    assert( l.get_points( 1 )[0] == p )

    assert( l.get_points( 2 )[0] == p )
    assert( l.get_points( 2 )[1] == p2 )

    assert( l.get_points( 3 )[0] == p )
    assert( l.get_points( 3 )[1] == p.point_on_segment( p2, 0.5 ) )
    assert( l.get_points( 3 )[2] == p2 )

    assert( l.get_points( 4 )[0] == p )
    assert( l.get_points( 4 )[1] == p.point_on_segment( p2, 1.0/3.0 ) )
    assert( l.get_points( 4 )[2] == p.point_on_segment( p2, 2.0/3.0 ) )
    assert( l.get_points( 4 )[3] == p2 )
