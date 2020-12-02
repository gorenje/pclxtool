import types, math, sys, re

from .point import *
from .bezier import *
from .geombase import geombase

# __all__ defines what should be accessible outside of this file
__all__ = [ "CenterPointEllipse", "SVGEllipse", "EllipseArc" ]

def _cpellipse_cubics():
    res = []
    pi4 = math.pi / 4.0

    sina = math.sin( pi4 )
    cosa = math.cos( pi4 )
    beta = 4.0 * (1.0 - cosa) / (3.0 * sina)

    pt1 = Point( cosa, -sina )
    pt4 = Point( cosa, sina )
    pt2 = Point( pt1.x + (beta * sina), pt1.y + (beta * cosa) )
    pt3 = Point( pt4.x + (beta * sina), pt4.y - (beta * cosa) )
    cb = CubicBezier( pt1, pt2, pt3, pt4 )

    for idx in range( 4 ):
        tcb = cb.clone()
        tcb.v_rotate( float((((idx*2)+1) * pi4)))
        res.append( tcb )

    return res

class CenterPointEllipse( geombase ):

    def __init__(self, cpt = Point.origin, radii_x = 0.0, radii_y = 0.0 ):
        self._cpt = cpt.clone()
        self._rx = radii_x
        self._ry = radii_y
        self._length = None
        self._beziers = None
        geombase.__init__(self)

    def __mul__(self,val):
        return CenterPointEllipse( self._cpt * val, self._rx * val,
                                   self._ry * val )
    def __sub__(self, pt ):
        return CenterPointEllipse( self._cpt - pt, self._rx, self._ry )

    def __repr__(self):
        return "CenterPointEllipse( %s, %s, %s )" \
               % ( repr(self._cpt), self._rx, self._ry )

    def get_points( self, point_count = 10 ):
        pts = []
        delta = (2.0 * math.pi) / float(point_count)
        rx = self._rx
        ry = self._ry
        cpt = self._cpt

        for idx in range( point_count ):
            pts.append( Point( rx * math.cos( delta * idx ) + cpt.x,
                               ry * math.sin( delta * idx ) + cpt.y ))

        return self._handleReverseStartPoint( pts )

    def length( self, time_step = 0.01 ):
        if self._length == None:
            self._length = 0
            for cb in self.to_cubic_beziers():
                self._length += cb.length(time_step)
        return self._length

    ## TODO: the returned value should be cloned before being returned
    def to_cubic_beziers(self):
        if self._beziers == None:
            self._beziers = _cpellipse_cubics()
            for cb in self._beziers:
                cb.v_scale( self._rx, self._ry )
                cb.v_translate( self._cpt )
        return self._beziers

class EllipseArc( geombase ):

    # constructor method
    # beg_angle and end_angle must be radians NOT degrees.
    def __init__(self, cpt = Point(), beg_angle = 0.0, end_angle = 2*math.pi,
                 radii_x = 0.0, radii_y = 0.0, xrotate = 0.0 ):
        self.center_pt = cpt.clone()
        self.beg_angle = beg_angle
        self.end_angle = end_angle
        self.radii_x = radii_x
        self.radii_y = radii_y
        self.xrotate = xrotate

        self.cubic_beziers = None
        self.quad_beziers = None
        geombase.__init__(self)

    def __mul__(self, val):
        return EllipseArc( self.center_pt * val, self.beg_angle,
                           self.end_angle, self.radii_x * val,
                           self.radii_y * val, self.xrotate )

    def __sub__(self, pt):
        return EllipseArc( self.center_pt - pt, self.beg_angle,
                           self.end_angle, self.radii_x,
                           self.radii_y, self.xrotate )

    def __repr__(self):
        return "EllipseArc( %s, %s, %s, %s, %s, %s )" \
               %(repr(self.center_pt), self.beg_angle, self.end_angle,
                 self.radii_x, self.radii_y, self.xrotate)

    # return cubic beziers for the representation of a unit arc as
    # defined by beg and end angle
    def __bezier_for_unit_arc( self ):
        res = []
        alpha = 0.5 * (self.end_angle - self.beg_angle)
        if alpha < 0:
            alpha += math.pi
        n = math.ceil( alpha * (4.0 / math.pi))
        if n > 1.0:
            alpha /= n
        if alpha < 1.0e-12:
            raise ValueError( "Alpha value too small: " + str( alpha ) )

        sina = math.sin( alpha )
        cosa = math.cos( alpha )
        beta = 4.0 * (1.0 - cosa) / (3.0 * sina)

        for idx in range( int( math.ceil(n) ) ):
            pt1 = Point( cosa, -sina )
            pt4 = Point( cosa, sina )
            pt2 = Point( pt1.x + (beta * sina), pt1.y + (beta * cosa) )
            pt3 = Point( pt4.x + (beta * sina), pt4.y - (beta * cosa) )
            cb = CubicBezier( pt1, pt2, pt3, pt4 )
            cb.v_rotate( self.beg_angle + float((((idx*2)+1)*alpha)))
            res.append( cb )
        return res

    # TODO: should return a *copy* of the original to avoid modification
    # TODO: of the original
    # return a series of cubic bezier curves which represent the
    # given in center point representation.
    def to_cubic_beziers( self ):
        if self.cubic_beziers == None:
            self.cubic_beziers = self.__bezier_for_unit_arc()
            for cb in self.cubic_beziers:
                cb.v_scale( self.radii_x, self.radii_y )
                cb.v_rotate( self.xrotate )
                cb.v_translate( self.center_pt )
        return self.cubic_beziers

    # get_points(..) and length(..) allow an ellipse to be passed to the
    # FlashSprite::followPath(...) method.
    def get_points( self, point_count = 10 ):
        cbs = self.to_cubic_beziers()
        length_per_point = float(self.length()) / float(point_count)
        pntcount = {}
        total_point_cnt = 0
        for bez in cbs:
            pntcount[bez] = int( math.floor(float(bez.length())\
                                            /float(length_per_point)))
            total_point_cnt += pntcount[bez]

        while total_point_cnt < point_count:
            for bez in cbs:
                pntcount[bez] += 1
                total_point_cnt += 1
                if total_point_cnt == point_count: break
        ret_val = []

        for bez in cbs: ret_val += bez.get_points( pntcount[bez] )

        return self._handleReverseStartPoint( ret_val )

    def length( self, time_step = 0.01 ):
        total_length = 0.0
        for cb in self.to_cubic_beziers(): total_length += cb.length(time_step)
        return total_length

####
# Code passed on the conversion of SVG ellipse definitions to center
# based ellipse definitions from the SVG 1.1 Specifications.
####

class SVGEllipse(EllipseArc):

    def __init__(self, spt = Point(), ept = Point(), xrotate = 0.0,
                 radii_x = 0.0, radii_y = 0.0,
                 large_arc_flag = 0, sweep_flag = 0 ):
        r_x,r_y = self.s2c_scale_radii( spt, ept, xrotate, radii_x, radii_y )
        xy_prime = self.s2c_x_y_prime( spt, ept, xrotate )
        center_prime = self.s2c_center_prime( r_x, r_y, xy_prime,
                                              large_arc_flag, sweep_flag )
        cpt = self.s2c_center( spt, ept, center_prime, xrotate )

        dtheta = self.s2c_delta_theta( spt, ept, xrotate, r_x, r_y,
                                       large_arc_flag, sweep_flag )
        dtheta = self.s2c_transform_delta_theta( dtheta, sweep_flag )

        if not sweep_flag:
            e_ang = self.s2c_theta_one( spt, ept, xrotate, r_x, r_y,
                                        large_arc_flag, sweep_flag )
            b_ang = e_ang + dtheta
        else:
            b_ang = self.s2c_theta_one( spt, ept, xrotate, r_x, r_y,
                                        large_arc_flag, sweep_flag )
            e_ang = b_ang + dtheta

        EllipseArc.__init__(self, cpt, b_ang, e_ang, r_x, r_y, xrotate)

    #### The following methods are used to convert a SVG representation of
    # of an ellipse to a center point representation. s2c == svg to center.
    #
    # this computes x-prime and y-prime as defined in the SVG v1.1
    # specifications in Appendix F, Figure 6.5.1., where:
    #   spt - start point of the ellipse arc
    #   ept - end point of the ellipse arc
    #   xrotate - the x-axis rotation
    # Return a point with x,y prime.
    def s2c_x_y_prime( self, spt, ept, xrotate ):
        diff = (spt - ept) / 2.0
        sin_phi = math.sin( xrotate )
        cos_phi = math.cos( xrotate )
        return Point( ( cos_phi * diff.x) + (sin_phi * diff.y), \
                      (-sin_phi * diff.x) + (cos_phi * diff.y) )

    # compute the center primes as defined in the SVG1.1 specifications,
    # in Appendix F, Figure 6.5.2, where:
    #   radii_{x,y} - are the radii values
    #   primecrd - prime coordinates. returned by s2c_x_y_prime
    #   large-arc flag - boolean value indicate whether this is a large-arc
    #   sweep flag - boolean value indicating the sweep status of ellipse
    # Return a center prime point
    def s2c_center_prime( self, radii_x, radii_y, primecrd,
                          large_arc_flag, sweep_flag ):
        rxsq = float( radii_x * radii_x )
        rysq = float( radii_y * radii_y )
        xpsq = float( primecrd.x * primecrd.x )
        ypsq = float( primecrd.y * primecrd.y )

        # topline
        factor = (rxsq*rysq) - (rxsq*ypsq) - (rysq*xpsq)
        # bottom line
        factor = abs( factor / ( (rxsq * ypsq) + (rysq * xpsq) ) )
        # sqrt
        factor = math.sqrt( factor )
        # sign
        if large_arc_flag == sweep_flag:
            factor = -factor

        return Point( factor * (  radii_x * primecrd.y / radii_y ), \
                      factor * ( -radii_y * primecrd.x / radii_x ) )

    # Return the center point given:
    #   spt - start point
    #   ept - end point
    #   cprime - center prime
    #   xrotate - x-axis rotation
    # Returns a point with the center coordinates
    def s2c_center( self, spt, ept, cprime, xrotate ):
        midpoint = Point( float(spt.x + ept.x) / 2.0,
                          float(spt.y + ept.y) / 2.0 )
        #midpoint = spt.midpoint( ept )
        cos_phi = math.cos( xrotate )
        sin_phi = math.sin( xrotate )
        return Point( (cos_phi*cprime.x) - (sin_phi*cprime.y) + midpoint.x,\
                      (sin_phi*cprime.x) + (cos_phi*cprime.y) + midpoint.y)

    # scale the radius values so that the ellipse reaches from ccrd to tcrd.
    # This is taken from SVG1.1 Specifications, Appendix F, Figures 6.6.{2,3}.
    def s2c_scale_radii( self, spt, ept, xrotate, radii_x, radii_y ):
        prmxy = self.s2c_x_y_prime( spt, ept, xrotate )

        sr = Point( radii_x, radii_y )

        diff  = (prmxy[0] * prmxy[0]) / (radii_x * radii_x)
        diff += (prmxy[1] * prmxy[1]) / (radii_y * radii_y)

        if diff > 1:
            sr = sr * math.sqrt( diff )

        return sr.x,sr.y

    # This computes theta_one as defined in the SVG 1.1 Specification,
    # Appendix F, Figures F.6.5.4 and F.6.5.5.
    def s2c_theta_one( self, spt, ept, xrotate, radii_x, radii_y,
                       large_arc_flag, sweep_flag ):
        prmxy = self.s2c_x_y_prime( spt, ept, xrotate )
        cprime = self.s2c_center_prime( radii_x, radii_y, prmxy,
                                        large_arc_flag, sweep_flag )
        pt1 = Point( 1, 0 )
        pt2 = (prmxy - cprime).v_scale( 1.0 / radii_x, 1.0 / radii_y )

        return pt1.v_svg_angle( pt2 )

    # Computes the value for delta theta as given in the SVG v1.1
    # specifications in Appendix F, Figures: 6.5.4 and 6.5.6.
    def s2c_delta_theta( self, spt, ept, xrotate, radii_x, radii_y,
                         large_arc_flag, sweep_flag ):
        prmxy = self.s2c_x_y_prime( spt, ept, xrotate )
        cprime = self.s2c_center_prime( radii_x, radii_y, prmxy,
                                        large_arc_flag, sweep_flag )

        pt1 = (prmxy - cprime).v_scale( 1.0 / radii_x, 1.0 / radii_y )
        pt2 = ((-prmxy) - cprime).v_scale( 1.0 / radii_x, 1.0 / radii_y )

        return pt1.v_svg_angle( pt2 )

    # Returns the transformed value of delta theta as described in the last
    # paragraph of the Appendex F, Section F.6.5 of the SVG v1.1 specifications
    # Where:
    #    dtheta - delta theta as returned by ea_get_delta_theta NOTE this
    #             value is in radians.
    #    sweep_flag - sweep flag
    # The transformed value of delta theta is returned in radians.
    def s2c_transform_delta_theta( self, dtheta, sweep_flag ):
        if (not sweep_flag) and dtheta > 0:
            return dtheta - (2.0 * math.pi)
        if sweep_flag and dtheta < 0:
            return dtheta + (2.0 * math.pi)
        return dtheta
