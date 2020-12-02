import types, math, sys, cmath, re

from .geombase import geombase

__all__ = [ # classes
            "Point",
            # Exceptions
            "SamePointsError", "LinesAreParallelError",
            "PointsVerticalError", "RatioIncorrectError",
            # global functions
            "assert_is_point", "assert_is_line",
            "assert_between_zero_one", "math_fractorial"
            ]

class SamePointsError(Exception):
    pass
class LinesAreParallelError(Exception):
    pass
class PointsVerticalError(Exception):
    pass
class RatioIncorrectError(Exception):
    pass

# this checks whether the given object has two attributes:
#   x - x coordinate value
#   y - y coordinate value
def assert_is_point( obj ):
    if not (hasattr( obj, "x" ) and hasattr( obj, "y" )):
        raise TypeError( "Object does not contain info for Point" )

def assert_is_line( obj ):
    if not( hasattr( obj,"c" ) and hasattr( obj,"slope" ) and \
            hasattr( obj,"yinsect" ) ):
        raise TypeError( "Object is not a line type" )

def assert_between_zero_one( val ):
    if val < 0.0 or val > 1.0:
        raise RatioIncorrectError( "Value not between 0 and 1: " + str(val) )

def math_fractorial( val = 0 ):
    res = 1
    for idx in range( int(val) ):
        res *= (idx+1)
    return res

###### Point/Vector class. This class can be used to represent points and
# vectors (vectors being assumed to represnet lines from 0,0 to coordinate
# value).
class Point(geombase):

    def __init__(self, x = 0.0, y = 0.0):
        self.x, self.y = x, y
        geombase.__init__(self)

    def __setitem__( self, key, value ):
        if key == 0 or key == 'x':     self.x = value
        elif key == 1 or key == 'y':   self.y = value

    # representation of a point
    def __repr__(self):
        return "Point(" + str(self.x) + ", " + str(self.y) + ")"

    def __str__(self):
        return "Point: X = " + str(self.x) + ", Y = " + str(self.y)

    def __add__(self, pt):
        if hasattr( pt, 'x' ) and hasattr( pt, 'y' ):
            return Point( self.x + pt.x, self.y + pt.y )
        return Point( self.x + pt, self.y + pt )
    __iadd__ = __add__

    def __sub__(self, pt):
        if hasattr( pt, 'x' ) and hasattr( pt, 'y' ):
            return Point( self.x - pt.x, self.y - pt.y )
        return Point( self.x - pt, self.y - pt )
    __isub__ = __sub__

    def __mul__(self, value):
        return Point( self.x * float(value), self.y * float(value) )

    def __div__(self, value):
        return (self * (1.0 / float(value)))

    def __neg__(self):
        return Point( -self.x, -self.y )

    def __pos__(self):
        return Point( +self.x, +self.y )

    def __abs__(self):
        return Point( abs(self.x), abs(self.y) )

    def __getitem__( self, key ):
        if key == 0 or key == 'x':     return self.x
        elif key == 1 or key == 'y':   return self.y
        return eval( "self." + str(key) )

    def __eq__(self, other):
        if other == None or \
               (not ( hasattr( other, "x" ) and hasattr( other, "y" ) )):
            return False
        return ( self.x == other.x and self.y == other.y )
#    __cmp__ = __eq__

    ### TODO: don't really want to use a hash based on the contents
    ### TODO: of the point, should be using the memory address
    def __hash__(self):
        return hash( repr( self ) )

    def __nonzero__(self):
        return ( self.x != 0 and self.y != 0 )

    # return the distance between the two points
    def distance( self, pt ):
        assert_is_point( pt )
        return (self - pt).v_length()

    # return the slope between the two points
    def slope( self, pt ):
        assert_is_point( pt )
        if self == pt:
            raise SamePointsError
        elif self.x == pt.x:
            raise PointsVerticalError
        return ( (self.y - pt.y) / (self.x - pt.x) )

    # reflect this point in the given point and return a new point with the
    # result
    def reflect( self, pt = None ):
        if pt == None: pt = Point.origin
        return Point( (2 * pt.x) - self.x, (2 * pt.y) - self.y )

    # return a new point that is the midpoint between the two given points
    def midpoint( self, pt ):
        return self.point_on_segment( pt, 0.500000000000 )

    # return a point that is located between this point and the given point
    # defined by ratio (value between 0 and 1 inclusive). If ratio is greater
    # than 1, then a point beyond the line joining the points is returned
    def point_on_segment( self, pt, ratio ):
        assert_is_point( pt )

        if self == pt:
            return Point( pt.x, pt.y )

        diff_x = ( float(self.x) - float(pt.x) ) * float( ratio )
        diff_y = ( float(self.y) - float(pt.y) ) * float( ratio )

        return self - Point( diff_x, diff_y )

    ###### Vector methods
    # return the length of the vector
    def v_length(self):
        return math.hypot( self.x, self.y )

    # return the dot product of this point and the other point. This assumes
    # that these points are vector points.
    def v_dot_product( self, pt ):
        assert_is_point( pt )
        return ( (self.x * pt.x) + (self.y * pt.y) )

    # return the angle between the two vectors. The value returned is in
    # radians ranging from 0 to 180
    def v_angle( self, pt ):
        assert_is_point( pt )
        return math.acos( self.v_dot_product( pt ) \
                          / (self.v_length() * pt.v_length()) )

    # return a new vector which is the rotation of this vector by rad radians
    def v_rotate( self, rad ):
        sina = math.sin( rad )
        cosa = math.cos( rad )
        return Point( (self.x * cosa) - (self.y * sina), \
                      (self.x * sina) + (self.y * cosa) )

    # Return a new vector which is a scaled version of this vector point
    def v_scale( self, factor_x, factor_y ):
        if hasattr( factor_x, 'x' ) and hasattr( factor_x, 'y' ):
            return Point( self.x * factor_x.x, self.y * factor_x.y )
        return Point( self.x * factor_x, self.y * factor_y )

    # return a new vector that has been translated by the dx and dy
    def v_translate( self, dx, dy ):
        if hasattr( dx, 'x' ) and hasattr( dx, 'y' ):
            return self + dx
        return self + Point( dx, dy )

    # this is the vector angle defined in the SVG specification:
    #  SVG v1.1 Specifcations, Appendix F, Figure F.6.5.4
    def v_svg_angle( self, pt ):
        assert_is_point( pt )
        sign = (((self.x*pt.y) - (self.y*pt.x)) >= 0)
        dprod = self.v_dot_product( pt )
        veclengths = self.v_length() * pt.v_length()
        acval = abs( math.acos( float(dprod) / float(veclengths) ) )
        if sign: return acval
        else:    return -acval

    # return a new point with the same coordinates as thie point
    def clone(self):
        return Point( self.x, self.y )

    ### These two allow a point to be passed into the Followpath method
    ### of the FlashSprite class
    def get_points( self, point_count = 10 ):
        ret_val = []
        pt = self.clone()
        for idx in range( point_count ): ret_val.append( pt )
        return ret_val
    def length( self, time_step = 0.01 ):
        # return a very small non-negative value, zero can cause
        # divide by zero errors.
        return 1e-12

    def to_svg(self):
        return "%s,%s" % (self.x, self.y)

Point.origin = Point( 0, 0 )

if __name__ == '__main__':
    p = Point( 1, 3 )
    assert(  repr(p.v_length()) == repr(3.1622776601683795))
    p2 = Point( 23, 23)
    assert( repr(p.v_angle( p2 )) == repr( 0.46364760900080643 ) )
    assert( repr(p.slope( p2 )) == repr(0.90909090909090906 ))
    assert( repr(p2.slope( p )) == repr(0.90909090909090906 ))
    p = Point( 1, 1 )
    p2 = p

    assert( p == p2 )

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

    p = Point( 5, 5 )
    assert( p.reflect() == Point( -5, -5 ) )
    assert( p.reflect( p.reflect() ) == Point( -15, -15 ) )
    p2 = Point( 10, 10 )
    assert( p.reflect( p2 ) == Point( 15, 15 ) )

    assert( (p == None) == False )
    assert( (p != None) == True )
