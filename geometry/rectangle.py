import types, math, sys, re

from .line import Line
from .point import Point
from .ellipse import SVGEllipse
from .geombase import geombase

# __all__ defines what should be accessible outside of this file
__all__ = [ "Rectangle" ]

class Rectangle(geombase):

    # insert any class variables here

    # constructor method
    def __init__(self, spt, width = 0.0, height = 0.0, rx = None, ry = None ):
        self._subshapes = []
        self._lpt = spt.clone()
        self._width = width
        self._height = height
        self._rx = rx
        self._ry = ry
        geombase.__init__(self)

        if width <= 0 and height <= 0:
            raise AttributeError("width and height less than or equal to zero")
        elif width <= 0:
            ept = spt + Point( 0, height )
            self._subshapes.append( Line( spt, ept ) )
            self._subshapes.append( Line( ept, spt ) )
        elif height <= 0:
            ept = spt + Point( width, 0 )
            self._subshapes.append( Line( spt, ept ) )
            self._subshapes.append( Line( ept, spt ) )
        elif rx == None and ry == None:
            pt1 = spt
            pt2 = spt + Point( width, 0 )
            pt3 = spt + Point( width, height )
            pt4 = spt + Point( 0, height )
            self._subshapes.append( Line(pt1,pt2) )
            self._subshapes.append( Line(pt2,pt3) )
            self._subshapes.append( Line(pt3,pt4) )
            self._subshapes.append( Line(pt4,pt1) )
        else:
            if rx == None:  rx = ry
            else:           ry = rx
            # check the r{x,y} values
            if rx < 0 or rx > float(width)/2.0:  rx = float(width) / 2.0
            if ry < 0 or ry > float(height)/2.0: ry = float(height) / 2.0

            self._subshapes.append(Line(spt+Point(rx,0),spt+Point(width-rx,0)))

            e = SVGEllipse( spt=spt+Point(width-rx,0), ept=spt+Point(width,ry),
                            xrotate=0, radii_x=rx,radii_y=ry, large_arc_flag=0,
                            sweep_flag=1 )
            self._subshapes.append( e )
            beziers = e.to_cubic_beziers()
            cpos = (beziers[len(beziers)-1])["anchor2"]
            self._subshapes.append( Line( cpos, spt+Point(width,height-ry) ) )

            e = SVGEllipse( spt+Point(width,height-ry),
                            spt+Point(width-rx,height), 0, rx,ry,0,1 )
            self._subshapes.append( e )
            beziers = e.to_cubic_beziers()
            cpos = (beziers[len(beziers)-1])["anchor2"]
            self._subshapes.append( Line( cpos, spt + Point( rx, height )))

            e = SVGEllipse( spt + Point( rx, height ),
                            spt+Point( 0, height-ry), 0, rx,ry, 0,1 )
            self._subshapes.append( e )
            beziers = e.to_cubic_beziers()
            cpos = (beziers[len(beziers)-1])["anchor2"]
            self._subshapes.append( Line( cpos, spt + Point( 0, ry ) ) )

            e = SVGEllipse( spt + Point( 0, ry ),
                            spt + Point( rx, 0 ), 0, rx,ry, 0,1 )
            self._subshapes.append( e )

    # scale shape
    def __mul__(self, val):
        if self._rx == None or self._ry == None:
            return Rectangle( self._lpt * val, self._width * val,
                              self._height * val, None, None )
        else:
            return Rectangle( self._lpt * val,self._width * val,
                              self._height * val, self._rx * val,
                              self._ry * val )
    # translate shape
    def __sub__(self, pt):
        return Rectangle( self._lpt - pt,self._width, self._height,
                          self._rx, self._ry )


    # representation method for debugging, return string
    def __repr__(self):
        return "Rectangle( %s, %s, %s, %s, %s )" \
               %(repr(self._lpt),str(self._width),str(self._height),
                 str(self._rx),str(self._ry))

    # string method returns an informal representation of the object
    def __str__(self):
        return repr(self)

    def get_points( self, point_count = 10 ):
        length_per_point = float(self.length()) / float(point_count)
        pntcount = {}
        total_point_cnt = 0
        for shp in self._subshapes:
            pntcount[shp] = int( math.floor(float(shp.length())\
                                            /float(length_per_point)))
            total_point_cnt += pntcount[shp]
        while total_point_cnt < point_count:
            for shp in self._subshapes:
                pntcount[shp] += 1
                total_point_cnt += 1
                if total_point_cnt == point_count: break
        ret_val = []
        for shp in self._subshapes: ret_val += shp.get_points( pntcount[shp] )

        return self._handleReverseStartPoint( ret_val )

    def clone(self):
        return Rectangle( self._lpt.clone(), self._width, self._height,
                          self._rx, self._ry )

    def length(self, time_step = 0.01 ):
        total_length = 0.0
        for shp in self._subshapes:
            total_length += shp.length( time_step )
        return total_length

    def getLeftHandPoint( self ):
        return self._lpt.clone()

    def getWidth( self ):
        return self._width

    def getHeight( self ):
        return self._height

    def get_shapes(self):
        return self._subshapes
