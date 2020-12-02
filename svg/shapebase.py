class ShapeBase:

    def __init__(self, attributes ):
        self._operations = []
        self.__attributes = attributes
        self.__di_opers = [] # display item operations to be executed once the display-item is available
        self._shapes = []

    def getOperations(self):
        return self._operations

    def getGeometry(self):
        return self._shapes

    def warning(self, msg):
        print("# WARNING: " + str(msg))

    def getAttribute( self, name, default=None ):
        if not name in self.__attributes:
            return default
        else:
            return self.__attributes[name].value
    def addAttributes( self, atts ):
        for idx in atts:
            self.__attributes[idx] = atts[idx]

    def get_di_opers(self):
        return self.__di_opers

    def add_di_oper(self,oper):
        self.__di_opers.append(oper)
