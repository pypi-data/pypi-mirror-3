import numpy

def fromroot(node):
    dtype = [('id', int),
             ('isroot', bool),
             ('isleaf', bool),
             ('label', numpy.string_),
             ('length', float),
             ('support', float),
             ('age', float),
             ('parent', int),
             ('left', int),
             ('right', int),
             ('treename', numpy.string_)]
    return numpy.array(
        [ (x.id,
           x.isroot,
           x.isleaf,
           x.label or "",
           x.length if x.length is not None else -1,
           x.support if x.support is not None else -1,
           x.age if x.age is not None else -1,
           x.parent.id if x.parent is not None else -1,
           x.left,
           x.right,
           x.treename or "") 
          for x in node ],
        dtype=numpy.dtype(dtype)
        )
           
