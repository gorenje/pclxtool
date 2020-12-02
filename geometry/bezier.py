import types, math, sys, cmath, re

from .point import *
from .geombase import geombase

__all__ = [ "GeneralBezier", "QuadraticBezier", "CubicBezier" ]

######## Bezier
# defines the functions required to define a bezier curve
class BezierBase:
    # #######
    # the maths for this is taken from:
    #      http://www.cs.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/ -->
    #                                                    Bezier/bezier-der.html
    # #######

    # point_number must not be > num_of_points. Time_value must be a value
    # between 0 and 1 inclusive
    def factor(self, num_of_points, point_number, time_value ):
        num_of_points -= 1
        ff = float( math_fractorial( num_of_points ) )
        ff /= float( math_fractorial( point_number ) \
                     * math_fractorial( num_of_points - point_number ) )
        tt = float( pow(time_value, point_number) )
        gg = float( pow(float(1.0 - time_value), num_of_points - point_number))
        return float(ff * tt * gg)

    # given an array of points and a time_value (between 0 and 1 (inc))
    # return a point along the Bezier curve.
    # The array of points must at least contain 3 points and it is assumed
    # that the first point (index = 0) and the last point are the two end
    # points.
    def _get_point( self, points, time_value ):
        res = Point( 0, 0 )
        num_of_points = len( points )
        if num_of_points < 3:
            raise Error( "num of points must be >= 3" )
        for idx in points:
            res += points[idx] * self.factor( num_of_points, idx, time_value )
        return res

    # returns the approximate length of the Bezier curve. This takes
    # successive points along the curve and measures the distance between
    # these points. The sum of these distances is returned.
    def _length( self, points, time_step = 0.01 ):
        dist = 0.0
        tme = 0
        pt = self._get_point( points, tme )
        while tme < 1.0:
            tme += time_step
            pt2 = self._get_point( points, tme )
            dist += pt.distance( pt2 )
            pt = pt2
        return dist

    ####
    # Derivative computations.
    # The following functions are used to compute derivative values for
    # the bezier curve
    def _q( self, points, n_value ):
        return ( points[n_value+1] - points[n_value] ) * n_value

    def _derivative_get_point( self, points, time_value ):
        res = Point( 0, 0 )
        num_of_points = len( points )
        for idx in range( num_of_points - 1 ):
            res += self._q( points, idx ) * \
                   self.factor( num_of_points - 1, idx, time_value )
        return res

class GeneralBezier(BezierBase, geombase):
    match_cp = re.compile( "cpt([0-9]+)" )

    def __init__(self, points):
        self.points = {}
        for pt in points: self.points[len(self.points)] = pt
        geombase.__init__(self)

    def __repr__(self):
        args = "[ " + repr( self.points[0] )
        for idx in range(1): args += ", " + repr( self.points[idx] )
        args += " ]"
        return "GeneralBezier( %s )" % args

    def __str__(self):
        res = "Bezier Curve with " + str( len( self.points ) ) + " Points:\n"
        res += "  Anchor1: " + str( self["anchor1"] ) + "\n"
        for idx in range( 1, len( self.points ) - 1 ):
            res += "  ConPoint %d: %s\n" % (idx, str( self["cpt%d" % idx] ))
        return res + "  Anchor2: " + str( self["anchor2"] ) + "\n"

    def __setitem__( self, key, value ):
        assert_is_point( value )
        pt = Point( value.x, value.y )
        mtch = self.match_cp.match( key )
        if key == "anchor1":
            self.points[0] = pt
        elif key == "anchor2":
            self.points[self.num_of_points() - 1] = pt
        # match the string 'cptXX' where is a number. This then returns
        # that control point. NOTE: control points are numbered from 1
        # although cpt0 is the same as anchor point 1
        elif mtch:
            self.points[int(mtch.group(1))] = pt
        else:
            raise KeyError(key)

    # multiple can be used to scale the bezier to something more useful!
    def __mul__(self, val):
        # note: the second map is only necessary becuase i was stupid enough
        # note: to use a dict instead of list to store the points ....
        pts = map( lambda v: v * val, map(lambda p: p[1], self.points.items()))
        return GeneralBezier( pts )

    # subtract used to translate a shape. The pt arguments must be a point
    # object
    def __sub__(self, pt):
        # note: the second map is only necessary becuase i was stupid enough
        # note: to use a dict instead of list to store the points ....
        pts = map( lambda v: v - pt, map(lambda p: p[1], self.points.items()))
        return GeneralBezier( pts )

    # this is a shortcut for accessing the anchor points and control points
    def __getitem__( self, key ):
        if   key == "anchor1":  return self.points[0]
        elif key == "anchor2":  return self.points[self.num_of_points() - 1]
        # match the string 'cptXX' where is a number. This then returns
        # that control point. NOTE: control points are numbered from 1
        # although cpt0 is the same as anchor point 1
        mtch = self.match_cp.match( key )
        if mtch:
            return self.points[ int(mtch.group(1)) ]
        return self.get_point( key )

    def clone(self):
        return self - Point.origin

    # return a point along the curve
    def get_point( self, time_value ):
        assert_between_zero_one( time_value )
        return self._get_point( self.points, time_value )

    # return point_count evenly spaced points on the curve. The default is to
    # return 10 points. Point 0 is the first anchor point, while the last
    # point is the last anchor point.
    def get_points( self, point_count = 10 ):
        ret_val = []
        if point_count <= 1:
            ret_val.append( self.get_point( 0.0 ) )
        else:
            for idx in range( point_count ):
                ret_val.append(self.get_point(float(idx)
                                              / float(point_count-1)))

        return self._handleReverseStartPoint( ret_val )

    def length( self, time_step = 0.01 ):
        return self._length( self.points, time_step )

    def num_of_points( self ):
        return len( self.points )

    def derivative_get_point( self, time_value ):
        assert_between_zero_one( time_value )
        return self._derivative_get_point( self.points, time_value )

    #### equivalent methods but applied to all points and does not create
    #### a new instance, rather does this "in house".
    def v_rotate( self, rad ):
        for idx in self.points:
            self.points[idx] = self.points[idx].v_rotate( rad )

    def v_scale( self, scale_x, scale_y=None ):
        for idx in self.points:
            self.points[idx] = self.points[idx].v_scale( scale_x, scale_y )

    def v_translate( self, dx, dy=None ):
        for idx in self.points:
            self.points[idx] = self.points[idx].v_translate( dx,dy )


class QuadraticBezier(GeneralBezier):
    def __init__(self, pt1, pt2, pt3):
        assert_is_point( pt1 )
        assert_is_point( pt2 )
        assert_is_point( pt3 )
        GeneralBezier.__init__(self, [ pt1, pt2, pt3 ] )

    def __mul__(self, val ):
        pts = map( lambda v: v * val, map(lambda p: p[1], self.points.items()))
        pts = [pt for pt in pts]
        return QuadraticBezier( pts[0], pts[1], pts[2] )

    def __sub__(self, pt ):
        pts = map( lambda v: v - pt, map(lambda p: p[1], self.points.items()))
        pts = [pt for pt in pts]
        return QuadraticBezier( pts[0], pts[1], pts[2] )

    def num_of_points(self):
        return 3

    def clone( self ):
        return QuadraticBezier( self.points[0].clone(),
                                self.points[1].clone(),
                                self.points[2].clone() )
    def __repr__(self):
        return "QuadraticBezier( %s, %s, %s )" \
               % (repr(self.points[0]), repr(self.points[1]),
                  repr(self.points[2]) )

class CubicBezier(GeneralBezier):
    def __init__(self, pt1, pt2, pt3, pt4):
        assert_is_point( pt1 )
        assert_is_point( pt2 )
        assert_is_point( pt3 )
        assert_is_point( pt4 )
        GeneralBezier.__init__(self, [ pt1, pt2, pt3, pt4 ] )

    def to_svg(self, rel = 1):
        char = 'C'
        if rel == 1: char = 'c'
        return "%s%s %s %s" % (char, self["cpt1"].to_svg(), self["cpt2"].to_svg(), self["anchor2"].to_svg())

    def __repr__(self):
        return "CubicBezier( %s, %s, %s, %s )" \
               % (repr(self.points[0]), repr(self.points[1]),
                  repr(self.points[2]), repr(self.points[3]))

    def __sub__(self, pt ):
        pts = map( lambda v: v - pt, map(lambda p: p[1], self.points.items()))
        pts = [pt for pt in pts]
        return CubicBezier( pts[0], pts[1], pts[2], pts[3] )

    def __mul__(self, val ):
        pts = map( lambda v: v * val, map(lambda p: p[1], self.points.items()))
        pts = [pt for pt in pts]
        return CubicBezier( pts[0], pts[1], pts[2], pts[3] )

    def num_of_points(self):
        return 4

    def clone( self ):
        return CubicBezier( self.points[0].clone(),self.points[1].clone(),
                            self.points[2].clone(),self.points[3].clone())

    # returns 4 quadratic bezier curves which are an approximation to
    # this cubic bezier
    def to_quad_beziers( self ):
        pa = self.points[0].point_on_segment( self.points[1], 3.0/4.0 )
        pb = self.points[3].point_on_segment( self.points[2], 3.0/4.0 )
        d = (self.points[3] - self.points[0]) * (1.0/16.0)

        pc1 = self.points[0].point_on_segment( self.points[1], 3.0/8.0 )
        pc2 = pa.point_on_segment( pb, 3.0/8.0 )
        pc2 = pc2 - d

        pc3 = pb.point_on_segment( pa, 3.0/8.0 )
        pc3 = pc3 + d

        pc4 = self.points[3].point_on_segment( self.points[2], 3.0/8.0 )

        pa1 = pc1.midpoint( pc2 )
        pa2 = pa.midpoint( pb )
        pa3 = pc3.midpoint( pc4 )

        res = []
        res.append( QuadraticBezier( self.points[0], pc1, pa1 ) )
        res.append( QuadraticBezier( pa1, pc2, pa2 ) )
        res.append( QuadraticBezier( pa2, pc3, pa3 ) )
        res.append( QuadraticBezier( pa3, pc4, self.points[3] ) )
        return res

if __name__ == '__main__':
    bz = BezierBase()
    points = {}
    points[0] = Point(  8, 10 )
    points[1] = Point( 10, 34 )
    points[2] = Point( 23, 45 )
    points[3] = Point( -23, -3 )

    points[4] = Point( 36.4,80.35 )
    points[5] = Point( 93.9,118.25 )
    points[6] = Point( 33.95,147 )

    points[7] = Point( 17.8,182.95 )
    points[8] = Point( 35.1,213.2 )

    cb = CubicBezier( points[0], points[1], points[2], points[3] )
    qb = QuadraticBezier( points[0], points[3], points[2] )

    qb1 = QuadraticBezier( points[4], points[5], points[6] )
    qb2 = QuadraticBezier( points[6], points[7], points[8] )

    print(cb.to_quad_beziers()[0])
    print(cb.to_quad_beziers()[1])
    print(cb.to_quad_beziers()[2])
    print(cb.to_quad_beziers()[3])

    print(cb.length())
    print(qb.length())

    print("Point @ 0.3: " + str(cb.get_point( 0.3 )))
    print("Der. Point @ 0.3: " + str(cb.derivative_get_point( 0.3 )))
    print("Point @ 0.3: " + str(qb.get_point( 0.3 )))
    print("Der. Point @ 0.3: " + str(qb.derivative_get_point( 0.3 )))

    assert( cb.num_of_points() == 4 )
    assert( qb.num_of_points() == 3 )
