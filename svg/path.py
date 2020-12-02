import types, math, sys, re, string

from geometry import *

from .shapebase import ShapeBase

# __all__ defines what should be accessible outside of this file
__all__ = [ "svg_path" ]

# Group but don't allow retrieval of their contents
def GROUP_F(s):        return "(?:" + s + ")"
def ONE_F(s):          return "(?:" + s + ")"
def ZERO_OR_ONE_F(s):  return "(?:" + s + ")?"
def ZERO_OR_MORE_F(s): return "(?:" + s + ")*"
def ONE_OR_MORE_F(s):  return "(?:" + s + ")+"
# Group which can be retrieved
def GROUP(s):          return "("  + s + ")"
def ONE(s):            return "("  + s + ")"
def ZERO_OR_ONE(s):    return "("  + s + ")?"
def ZERO_OR_MORE(s):   return "("  + s + ")*"
def ONE_OR_MORE(s):    return "("  + s + ")+"

def assertEqual( obj1, obj2 ):
    if not obj1 == obj2:
        raise AssertionError("'" + str(obj1) + "' != '" + str(obj2) + "'")

class svg_path(ShapeBase):

    # insert any class variables here
    OR = "|"
    dot = "[.]"
    sign = "[+-]"
    digit = "[0-9]"
    dig_seq = ONE_OR_MORE_F(digit)
    int_const = dig_seq

    ## Note: when using OR make sure that the longest matches come first:
    ## OR (in python) is non-greedy (that is to say: it's a sozialist!)

    frac_const = GROUP_F( ZERO_OR_ONE_F(dig_seq) + dot + ONE_F(dig_seq) ) \
                 + OR + GROUP( ONE(dig_seq) + dot )

    exponent = "[eE]" + ZERO_OR_ONE_F(sign) + dig_seq

    fp_const = GROUP_F( ONE_F(frac_const) + ZERO_OR_ONE_F(exponent) ) \
               + OR + GROUP_F( ONE_F(dig_seq) + ONE_F(exponent) )

    number = GROUP( ZERO_OR_ONE(sign) + ONE(fp_const) ) \
             + OR + GROUP( ZERO_OR_ONE(sign) + ONE(int_const) )

    actions = GROUP("[MmAaTtQqSsCcVvHhLlZz]")

    re_num = re.compile( number )

    # constructor method
    def __init__(self, attributes):
        ShapeBase.__init__(self, attributes)
        self.__data = self.getAttribute( "d", "" )
        self.__cpos = None # current position in absolute coordinates
        self.__ccpt = None # current control point if one is set
        self.__ipos = None # store any initial position, i.e. this is the first position that was set.
        self.__pname = None # production name, i.e. the MmAaCc...
        self.__prev_cpos = None # previously set position. set when a closepath is executed
        self.parse_data_string()

        ## handle any transform specification
        transform = self.getAttribute( "transform", "" )
        if transform != "":
            transform = re.sub( "\s+", ",", transform)
            transform = re.sub( "matrix", "setMatrix", transform )
            transform = re.sub( "translate", "moveTo", transform )
            self.add_di_oper( transform )

    # destructor method
    def __del__(self):
        pass

    def str2flts( self, val_string ):
        return self.__value2floats( val_string )

    def __value2floats( self, val_string ):
        # could check the end and start values to make sure that no
        # data is lost (of course would have to check that is data is non
        # whitespace).
        val = []
        mo = self.re_num.search(val_string)
        while not mo == None:
            val.append( float( mo.group() ) )
            val_string = val_string[mo.end():]
            mo = self.re_num.search(val_string)
        return val

    def parse_data_string( self ):
        # replace multiple whitespace with a single space and remove
        # leading and trailing whitespace
        # self.__data = string.strip(re.sub(re.compile("\s+")," ",self.__data))
        self.__data = str(re.sub(re.compile("\s+")," ",self.__data)).strip()
        # split the data string on the actions
        elems = re.split( self.actions, self.__data )
        # reorganise the list that was returned
        operations = []
        start_idx=0
        if elems[0] == '': start_idx = 1
        for idx in range(start_idx,len(elems),2):
            operations.append( [ elems[idx], elems[idx+1] ] )
        for a,v in operations:
            eval("self.handle_" + a + "(" + str(self.__value2floats(v)) + ")")

    # convert relative to absolute coordinates
    def __rel2abs( self, pt ):
        return self.cpos() + pt

    def cpos(self):
        if self.__cpos == None and self.__prev_cpos == None:
            raise Error("No current position defined")
        elif self.__cpos == None and self.__prev_cpos != None:
            self.__cpos = self.__prev_cpos.clone()
            self.__ipos = self.__prev_cpos.cline()
            self.__prev_cpos = None
        return self.__cpos

    # set the current position
    def __setCurrentPosition( self, pt ):
        if pt == None:
            if self.__ipos != None:
                self.__prev_cpos = self.__ipos.clone()
            self.__cpos = None
            self.__ipos = None
        else:
            if self.__cpos == None:
                self.__ipos = pt.clone()
            self.__cpos = pt.clone()

    def __setup_current_position(self):
        if self.__cpos == None and self.__prev_cpos == None:
            self.__setCurrentPosition(Point(0,0))

    def __setControlPoint( self, pt ):
        if pt == None:    self.__ccpt = None
        else:             self.__ccpt = pt.clone()

    def __setProdName( self, char ):
        self.__pname = char

    def __warning( self, msg ):
        print("# WARNING: " + str(msg))

    def __check_idx( self, fname, expect, have ):
        if expect == 0:
            if have > 0:
                self.__warning("%s: ignoring values %d < %d" % (fname,expect,
                                                                have))
        elif expect > have:
            raise AttributeError("%s: not enough data %d > %d"%(fname,expect,
                                                                have))
        elif have % expect != 0:
            self.__warning( "%s: ignoring values %d %% %d == %d"\
                            %(fname,have,expect,have%expect))

    def handle_M(self, values ):
        self.__check_idx( "handle_m", 1, len(values) )
        abspt = Point( values[0], values[1] )
        self._operations.append( "moveTo( %s ) # handle_M" % repr(abspt) )
        self._shapes.append( abspt )
        self.__setProdName( "M" )
        self.__setCurrentPosition( abspt )
        self.__setControlPoint( None )
        if len(values) > 2:
            self.handle_L( values[2:] )

    def handle_m(self, values ):
        self.__check_idx( "handle_m", 1, len(values) )

        # if cpos is not yet set, then this is probably the very first element
        # in the path. Set cpos to 0,0
        self.__setup_current_position()

        abspt = self.__rel2abs( Point( values[0], values[1] ) )
        self._operations.append( "moveTo( %s ) # handle_m" % repr( abspt ))
        self._shapes.append( abspt )
        self.__setProdName( "m" )
        self.__setControlPoint( None )
        self.__setCurrentPosition( abspt )
        if len( values ) > 2:
            self.handle_l( values[2:] )

    def handle_A(self, values ):
        self.__check_idx( "handle_A", 7, len(values) )
        for idx in range( 0, len(values), 7 ):
            radii_x = abs( values[idx] )
            radii_y = abs( values[idx+1] )
            xrotate = values[idx+2] % 360
            flags = [ values[idx+3], values[idx+4] ]
            tpt = Point( values[idx+5], values[idx+6] )

            if tpt == self.cpos():
                self.__warning( "handle_A: target and current point same" )
                continue

            if radii_x == 0 or radii_y == 0:
                self.__warning("handle_A: one or both radii zero, doing line")
                self.handle_L( [ tpt.x, tpt.y ] )
                self.__setProdName( "A" )
                continue

            ellip_str = "SVGEllipse(%s,%s,%s,%s,%s,%s,%s)" \
                        % (repr(self.cpos()),repr(tpt),str(xrotate),
                           str(radii_x),str(radii_y),str(flags[0]),
                           str(flags[1]))
            self._operations.append( "drawEllipse(%s) # handle_A" % ellip_str)
            self._shapes.append( eval( ellip_str ) )
            self.__setCurrentPosition( tpt )
            self.__setProdName( "A" )

    def handle_a(self, values ):
        self.__check_idx( "handle_a", 7, len(values) )
        for idx in range( 0, len(values), 7 ):
            radii_x = abs( values[idx] )
            radii_y = abs( values[idx+1] )
            xrotate = values[idx+2] % 360
            flags = [ values[idx+3], values[idx+4] ]
            tpt = self.__rel2abs( Point( values[idx+5], values[idx+6] ) )

            if tpt == self.cpos():
                self.__warning( "handle_a: target and current point same" )
                continue

            if radii_x == 0 or radii_y == 0:
                self.__warning("handle_a: one or both radii zero, doing line")
                self.handle_L( [ tpt.x, tpt.y ] )
                self.__setProdName( "a" )
                continue

            ellip_str = "SVGEllipse(%s,%s,%s,%s,%s,%s,%s)"\
                        % (repr(self.cpos()),repr(tpt),str(xrotate),
                           str(radii_x),str(radii_y),str(flags[0]),
                           str(flags[1]))

            self._operations.append("drawEllipse(%s) # handle_a" % ellip_str)
            self._shapes.append( eval( ellip_str ) )
            self.__setCurrentPosition( tpt )
            self.__setProdName( "a" )

    def handle_T(self, values ):
        self.__check_idx( "handle_T", 2, len(values))
        for idx in range( 0, len(values), 2 ):
            if self.__pname in [ "t", "q", "T", "Q" ]:
                cntpt = self.__ccpt.reflect( self.cpos() )
            else:
                if self.cpos() != None:
                    cntpt = self.cpos().clone()
                else:
                    self.__warning( "handle_T: no current point defined" )
                    cntpt = Point( values[idx], values[idx+1] )

            apt = Point( values[idx], values[idx+1] )
            self._operations\
            .append("drawQuadBezier( %s, %s, %s ) # handle_T" \
                    % ( repr(self.cpos()), repr(cntpt), repr(apt) ))
            self._shapes.append( eval( "QuadraticBezier( %s,%s,%s)"\
                                       %(repr(self.cpos()), repr(cntpt),
                                         repr(apt))))
            self.__setControlPoint( cntpt )
            self.__setCurrentPosition( apt )
            self.__setProdName( "T" )


    def handle_t(self, values ):
        self.__check_idx( "handle_t", 2, len(values) )
        for idx in range( 0, len(values), 2 ):
            if self.__pname in [ "t", "q", "T", "Q" ]:
                cntpt = self.__ccpt.reflect( self.cpos() )
            else:
                if self.cpos() != None:
                    cntpt = self.cpos().clone()
                else:
                    self.__warning( "handle_t: no current point defined" )
                    cntpt = Point( values[idx], values[idx+1] )

            apt = self.__rel2abs( Point( values[idx], values[idx+1] ) )
            self._operations\
            .append("drawQuadBezier( %s, %s, %s ) # handle_t" \
                    % (repr(self.cpos()), repr(cntpt), repr(apt)))
            self._shapes.append( eval( "QuadraticBezier( %s,%s,%s)"\
                                       %(repr(self.cpos()), repr(cntpt),
                                         repr(apt))))
            self.__setControlPoint( cntpt )
            self.__setCurrentPosition( apt )
            self.__setProdName( "t" )

    def handle_Q(self, values ):
        self.__check_idx( "handle_Q", 4, len(values) )
        for idx in range( 0, len(values), 4 ):
            cntpt = Point( values[idx], values[idx+1] )
            apt = Point(values[idx+2], values[idx+3] )
            self._operations\
            .append("drawQuadBezier( %s, %s, %s ) # handle_Q" \
                    % ( repr(self.cpos()), repr(cntpt), repr(apt) ))
            self._shapes.append( eval( "QuadraticBezier( %s,%s,%s)"\
                                       %(repr(self.cpos()), repr(cntpt),
                                         repr(apt))))
            self.__setControlPoint( cntpt )
            self.__setCurrentPosition( apt )
            self.__setProdName( "Q" )

    def handle_q(self, values ):
        self.__check_idx( "handle_q", 4, len(values) )
        for idx in range( 0, len(values), 4 ):
            cntpt = self.__rel2abs( Point( values[idx], values[idx+1] ))
            apt = self.__rel2abs( Point(values[idx+2], values[idx+3] ))
            self._operations\
            .append("drawQuadBezier( %s, %s, %s ) # handle_q" \
                    % (repr(self.cpos()), repr(cntpt), repr(apt)))
            self._shapes.append( eval( "QuadraticBezier( %s,%s,%s)"\
                                       %(repr(self.cpos()), repr(cntpt),
                                         repr(apt))))
            self.__setControlPoint( cntpt )
            self.__setCurrentPosition( apt )
            self.__setProdName( "q" )


    def handle_S(self, values ):
        self.__check_idx( "handle_S", 4, len(values) )
        for idx in range( 0, len(values), 4 ):
            if self.__pname in [ "c", "s", "C", "S" ]:
                cntpt1 = self.__ccpt.reflect( self.cpos() )
            else:
                cntpt1 = self.cpos().clone()
            cntpt2 = Point( values[idx], values[idx+1] )
            apt2 = Point( values[idx+2], values[idx+3] )
            self._operations\
            .append( "drawCubicBezier( %s, %s, %s, %s ) # handle_S" \
                     %(repr(self.cpos()),repr(cntpt1),repr(cntpt2),repr(apt2)))
            self._shapes.append( eval( "CubicBezier(%s,%s,%s,%s)"\
                                       %(repr(self.cpos()),repr(cntpt1),
                                         repr(cntpt2),repr(apt2))))
            self.__setCurrentPosition( apt2 )
            self.__setControlPoint( cntpt2 )
            self.__setProdName( "S" )

    def handle_s(self, values ):
        self.__check_idx( "handle_s", 4, len(values) )
        for idx in range( 0, len(values), 4 ):
            if self.__pname in [ "c", "s", "C", "S" ]:
                cntpt1 = self.__ccpt.reflect( self.cpos() )
            else:
                cntpt1 = self.cpos().clone()
            cntpt2 = self.__rel2abs(Point( values[idx], values[idx+1] ))
            apt2 = self.__rel2abs(Point( values[idx+2], values[idx+3] ))
            self._operations\
            .append("drawCubicBezier( %s, %s, %s, %s ) # handle_s" \
                    % (repr(self.cpos()),repr(cntpt1),repr(cntpt2),repr(apt2)))
            self._shapes.append( eval( "CubicBezier(%s,%s,%s,%s)"\
                                       %(repr(self.cpos()),repr(cntpt1),
                                         repr(cntpt2),repr(apt2))))
            self.__setCurrentPosition( apt2 )
            self.__setControlPoint( cntpt2 )
            self.__setProdName( "s" )


    def handle_C(self, values ):
        self.__check_idx( "handle_C", 6, len(values) )
        for idx in range( 0, len(values), 6 ):
            cntpt1 = Point( values[idx],   values[idx+1] )
            cntpt2 = Point( values[idx+2], values[idx+3] )
            apt2   = Point( values[idx+4], values[idx+5] )
            self._operations\
            .append("drawCubicBezier( %s, %s, %s, %s ) # handle_C" \
                    % (repr(self.cpos()),repr(cntpt1),repr(cntpt2),repr(apt2)))
            self._shapes.append( eval( "CubicBezier(%s,%s,%s,%s)"\
                                       %(repr(self.cpos()),repr(cntpt1),
                                         repr(cntpt2),repr(apt2))))
            self.__setCurrentPosition( apt2 )
            self.__setControlPoint( cntpt2 )
            self.__setProdName( "C" )

    def handle_c(self, values ):
        self.__check_idx( "handle_c", 6, len(values) )
        for idx in range( 0, len(values), 6 ):
            cntpt1 = self.__rel2abs( Point( values[idx],   values[idx+1] ) )
            cntpt2 = self.__rel2abs( Point( values[idx+2], values[idx+3] ) )
            apt2   = self.__rel2abs( Point( values[idx+4], values[idx+5] ) )
            self._operations\
            .append("drawCubicBezier( %s, %s, %s, %s ) # handle_c" \
                    % (repr(self.cpos()),repr(cntpt1),repr(cntpt2),repr(apt2)))
            self._shapes.append( eval( "CubicBezier(%s,%s,%s,%s)"\
                                       %(repr(self.cpos()),repr(cntpt1),
                                         repr(cntpt2),repr(apt2))))
            self.__setCurrentPosition( apt2 )
            self.__setControlPoint( cntpt2 )
            self.__setProdName( "c" )


    def handle_V(self, values ):
        tvalues = []
        cpos = self.cpos()
        for val in values:
            tvalues.append( cpos.x )
            tvalues.append( val )
        self.handle_L( tvalues, "V" )

    def handle_v(self, values ):
        tvalues = []
        cpos = self.cpos()
        for val in values:
            tvalues.append( cpos.x )
            tvalues.append( cpos.y + val )
        self.handle_L( tvalues, "v" )


    def handle_H(self, values ):
        tvalues = []
        cpos = self.cpos()
        for val in values:
            tvalues.append( val )
            tvalues.append( cpos.y )
        self.handle_L( tvalues, "H" )

    def handle_h(self, values ):
        tvalues = []
        cpos = self.cpos()
        for val in values:
            tvalues.append( cpos.x + val )
            tvalues.append( cpos.y )
        self.handle_L( tvalues, "h" )


    def handle_L(self, values, fname="L" ):
        self.__check_idx( "handle_%s"%fname, 2, len(values) )
        for idx in range( 0, len(values), 2 ):
            pt = Point( values[idx], values[idx+1] )
            self._operations.append("lineTo( %s ) # handle_%s"
                                      % (repr(pt),fname) )
            self._shapes.append( Line( self.cpos(), pt ) )
            self.__setProdName( fname )
            self.__setCurrentPosition( pt )
            self.__setControlPoint( None )

    def handle_l(self, values ):
        self.__check_idx( "handle_l", 2, len(values) )
        for idx in range( 0, len(values), 2 ):
            pt = self.__rel2abs( Point( values[idx], values[idx+1] ) )
            self._operations.append( "lineTo( %s ) # handle_l" % repr(pt))
            self._shapes.append( Line( self.cpos(), pt ) )
            self.__setProdName( "l" )
            self.__setCurrentPosition( pt )
            self.__setControlPoint( None )

    def handle_Z(self, values ):
        self.__check_idx( "handle_Z", 0, len(values) )
        self._operations.append( "lineTo( %s ) # %s"
                                  % (repr(self.__ipos), "handle_Z"))
        try:
            self._shapes.append( Line( self.cpos(), self.__ipos) )
        except SamePointsError:
            pass
        self.__setCurrentPosition( None )
        self.__setControlPoint( None )
        self.__setProdName( "Z" )

    def handle_z(self, values ):
        self.__check_idx( "handle_z", 0, len(values) )
        self._operations.append("lineTo( %s ) # handle_z" % repr(self.__ipos))
        try:
            self._shapes.append( Line( self.cpos(), self.__ipos) )
        except SamePointsError:
            pass
        self.__setCurrentPosition( None )
        self.__setControlPoint( None )
        self.__setProdName( "z" )

# define a main function that
def main():
    rc = re.compile( Path.number )
    tests = { "a132.."   : "132.",
              ".11.2.12" : ".11",
              "21.2e2a"  : "21.2e2",
              "+1.22.ds" : "+1.22",
              "-1.2"     : "-1.2",
              "-.143"    : "-.143",
              ".111"     : ".111",
              "+.2"      : "+.2",
              "a+0.2"    : "+0.2",
              "asdasd"   : None }
    for tst in tests:
        mo = rc.search( tst )
        if mo != None:
            print(tst + ": " +str(mo.start()) + " --> " + str(mo.end()))
        if not mo == None:    assertEqual( tests[tst], mo.group() )
        else:                 assertEqual( tests[tst], None )

if __name__ == '__main__':
    main()
