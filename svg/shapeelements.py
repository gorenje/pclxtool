import types, math, sys, re

from geometry import *

from .path import *

from .shapebase import ShapeBase

# __all__ defines what should be accessible outside of this file
__all__ = [ "svg_rect", "svg_circle",  "svg_ellipse",
            "svg_line", "svg_polygon", "svg_polyline",
            "svg_text", "svg_tspan",   "svg_image" ]

class svg_circle(ShapeBase):
    def __init__(self, attributes):
        ShapeBase.__init__( self, attributes )
        r = self.getAttribute( "r" )
        if r == None or float(r) <= 0.0:
            self.warning( "circle: radius not defined or negative" )
            return
        cx = self.getAttribute("cx","0")
        cy = self.getAttribute("cy","0")
        self._operations.append( "moveTo( Point( %s, %s ) ) # circle" \
                                  % ( cx, cy ) )
        self._operations.append( "drawCircle( int(%s) ) # circle" % r )
        self._shapes.append( eval( "Circle( Point(%s,%s), %s )" % (cx,cy,r)))

class svg_line(ShapeBase):
    def __init__( self, attributes ):
        ShapeBase.__init__(self, attributes )
        x1 = self.getAttribute( "x1", "0" )
        x2 = self.getAttribute( "x2", "0" )
        y1 = self.getAttribute( "y1", "0" )
        y2 = self.getAttribute( "y2", "0" )
        self._operations.append("moveTo( Point( %s,%s )) # line"%(x1,y1))
        self._operations.append("lineTo( Point( %s,%s )) # line"%(x2,y2))
        self._shapes.append( eval("Line(Point(%s,%s),Point(%s,%s))" \
                                  %(x1,y1,x2,y2)))
class svg_rect(ShapeBase):
    def __init__(self, attributes ):
        ShapeBase.__init__(self, attributes )
        width = self.getAttribute( "width", None )
        height = self.getAttribute( "height", None )
        if width == None or height == None:
            self.warning( "rectangle: width or height not defined" )
            return
        lpx = self.getAttribute("x","0")
        lpy = self.getAttribute("y","0")
        rx = self.getAttribute( "rx", None )
        ry = self.getAttribute( "ry", None )
        self._operations\
         .append( "drawRectangle( Point(%s,%s), %s, %s, %s, %s) # rectangle"\
                  %(lpx, lpy, width, height, rx, ry ))
        self._shapes.append( eval( "Rectangle( Point(%s,%s),%s,%s,%s,%s)" \
                                   % (lpx, lpy, width, height, rx, ry )))

class svg_ellipse(ShapeBase):
    def __init__(self, attributes ):
        ShapeBase.__init__(self, attributes )
        rx = self.getAttribute( "rx", None )
        ry = self.getAttribute( "ry", None )
        if rx == None or float(rx) <= 0.0:
            self.warning( "ellipse: radii X value incorrect: '" +str(rx)+"'")
            return
        if ry == None or float(ry) <= 0.0:
            self.warning( "ellipse: radii Y value incorrect: '" +str(rx)+"'")
            return
        cx = self.getAttribute( "cx", "0" )
        cy = self.getAttribute( "cy", "0" )
        self._operations\
         .append(("drawEllipse(CenterPointEllipse(cpt=Point(%s,%s),radii_x=%s,"
                   + "radii_y=%s))")%(cx,cy,rx,ry))
        self._shapes.append( eval(("CenterPointEllipse(cpt=Point(%s,%s),"
                                   + "radii_x=%s,radii_y=%s)")%(cx,cy,rx,ry)))

class svg_polyline(ShapeBase):
    def __init__(self, attributes):
        ShapeBase.__init__(self, attributes)
        pts = self.getAttribute( "points", None )
        if pts == None: return
        pth = path.svg_path( "" )
        vals = pth.str2flts( pts )
        pt = Point( float(vals[0]), float(vals[1]))
        self._operations.append( "moveTo(%s)"%repr(pt) )
        for idx in range(2, len(vals), 2):
            pt2 = eval( "Point( %s, %s )" % (str(vals[idx]), str(vals[idx+1])))
            if pt == pt2:
                print("# WARNING: ignoring line because points are the same")
            else:
                self._shapes.append( Line( pt, pt2 ) )
                self._operations.append( "lineTo(%s)" % repr(pt2) )
                pt = pt2

class svg_polygon(ShapeBase):
    def __init__(self, attributes):
        ShapeBase.__init__(self, attributes)
        pts = self.getAttribute( "points", None )
        if pts == None: return
        pth = path.svg_path( "" )
        vals = pth.str2flts( pts )
        pt = Point( float(vals[0]), float(vals[1]))
        first_pt = pt.clone()
        self._operations.append( "moveTo(%s)"%repr(pt) )
        for idx in range(2, len(vals), 2):
            pt2 = eval( "Point( %s, %s )" % (str(vals[idx]), str(vals[idx+1])))
            self._operations.append( "lineTo(%s)" % repr(pt2))
            self._shapes.append( Line( pt, pt2 ) )
            pt = pt2
        # sometimes we get the same point (as last point) as the first point
        if not pt == first_pt:
            self._operations.append( "lineTo(%s)"%repr(first_pt) )
            self._shapes.append( Line( pt, first_pt ) )

class svg_text(ShapeBase):
    def __init__(self, attributes):
        ShapeBase.__init__(self, attributes )
    def set_text(self,text):
        self.__text__ = text
    def set_tspan(self, tspan_obj ):
        ## hardcode font, can be changed
        ##    tspan_obj.getAttribute( 'font-family' )
        self._operations.append( "setFont( SWFFont( 'Arial.fdb' ) )" )
        self._operations.append( "setHeight( %s )" % tspan_obj.getAttribute( "font-size","10" ) )
        self._operations.append( "setColor(getColor('%s'))" % tspan_obj.getAttribute( "fill", "#000000"))
        self._operations.append( "setSpacing( 0 )")
        self._operations.append( "moveTo( %s, %s )" % (tspan_obj.getAttribute( "x","0" ), tspan_obj.getAttribute( "y", "0" ) ) )
        self._operations.append( "addString('%s')" % re.compile( "\s+" ).sub( " ", tspan_obj.get_text().strip()  ))
        ## returns displayitem operations
        di_opers = []
        ## assume that the transform contains a matrix
        transform = self.getAttribute( "transform", "" )
        if transform != "":
            transform = re.sub( "\s+", ",", transform)
            transform = re.sub( "matrix", "setMatrix", transform )
            di_opers.append( transform )
        return di_opers

class svg_tspan(ShapeBase):
    def __init__(self, attributes):
        ShapeBase.__init__(self, attributes )
    def set_text(self,text):
        self.__text__ = text
    def get_text(self):
        return self.__text__

class svg_image(ShapeBase):
    def __init__(self, attributes):
        ShapeBase.__init__(self, attributes )
        self._operations.append( "moveTo( Point(%s, %s) )" % (self.getAttribute( "x", "0" ),
                                                              self.getAttribute("y", "0")))
        self.__di_opers = []
        ## assume that the transform contains a matrix
        transform = self.getAttribute( "transform", "" )
        if transform != "":
            transform = re.sub( "\s+", ",", transform)
            transform = re.sub( "matrix", "setMatrix", transform )
            self.__di_opers.append( transform )

    def get_di_opers(self):
        return self.__di_opers
