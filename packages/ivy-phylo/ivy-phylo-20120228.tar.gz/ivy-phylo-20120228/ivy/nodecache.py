import numpy

class NodeCache:
    def __init__(self, root):
        array = numpy.array; nan = numpy.nan
        self.root = root
        nodes = array([ x for x in root ])
        self.node = nodes
        self.id = array([ x.id for x in nodes])
        self.label = array([ x.label or "" for x in nodes ])
        self.length = array([ x.length if x.length is not None else nan
                              for x in nodes ])
        self.support = array([ x.support if x.support is not None else nan
                               for x in nodes ])
        self.parent = array([ x.parent.id if x.parent else nan for x in nodes ])
        self.left = array([ x.left if x.left is not None else nan
                            for x in nodes ])
        self.right = array([ x.right if x.right is not None else nan
                             for x in nodes ])
        
