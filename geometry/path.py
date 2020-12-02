import types, math, sys, re

from .geombase import geombase

from .point import Point
from .rectangle import Rectangle
from .circle import Circle

# __all__ defines what should be accessible outside of this file
__all__ = [ "Path" ]

class Path( list, geombase ):

    # insert any class variables here

    # constructor method
    def __init__(self, lst = []):
        geombase.__init__(self)
        list.__init__(self, lst)

    # destructor method
    def __del__(self):
        pass

    def __repr__(self):
        return "Path( " + list.__repr__(self) + ")"
    __str__ = __repr__

    # multiple operator which performs a scaling of the path segments
    # contained in the path. This does not modify the original path rather
    # it returns new path object.
    def __mul__(self, factor ):
        return Path( map( lambda val: val * factor, self ) )

    # generate a new path which is the translation of the original path by the
    # given point. The original path is not modified
    def __sub__(self, pt ):
        return Path( map( lambda val: val - pt, self ) )

    # this does a translation of the path segments by the given point. This
    # modifies this path and returns a reference to itself.
    def translate( self, pt ):
        for idx in range( len(self) ):
            self[idx] = self[idx] - pt
        return self

    # this scales the existing path by the given factor. This modifies the
    # path instance and returns a reference to itself.
    def scale( self, factor ):
        for idx in range( len(self) ):
            self[idx] = self[idx] * factor
        return self

    # reversing a path is not just a matter of reversing the order but also
    # the individual shapes, therefore propagate this call to the shapes and
    # then call the list.reverse(..).
    # BTW: this modifies the path
    def reverse( self ):
        for idx in range( len(self) ):
            self[idx].reverse()
        list.reverse( self )

    def clone(self):
        return Path( map( lambda val: val.clone(), self ) )

    # this prevents slices (i.e. Path([1,2,3])[1:]) from returning lists
    # rather they return a new Path object
    def __getitem__(self, index):
        obj = list.__getitem__( self, index )
        if type(obj) == list: return Path(obj)
        else:                 return obj

    def __getslice__(self, i, j):
        return self[max(0, i):max(0, j):]

    def __setslice__(self, i, j, seq):
        self[max(0, i):max(0, j):] = seq

    def __delslice__(self, i, j):
        del self[max(0, i):max(0, j):]

# define a main function
def main():

    p = Path()
    p.append( Point.origin )

    p.append( Rectangle( Point.origin, 10, 10 ) )
    p.append( Circle( Point.origin, 10 ) )

    p3 = p - Point(1,2)
    print( p3)
    print( p3[0] == p[0])
    print( p)

    p2 = p * 1.2

    print( p2)

    print( p)

    p.scale( 1.2 )

    print( p)
    print( repr(p))

    print( p[1:])

if __name__ == '__main__':
    main()
