from igraph import Graph

def fromtree(root):
    nodes = list(root)
    N = len(nodes)
    edges = [ (x.id-1, x.parent.id-1) for x in nodes[1:] ]
    g = Graph(N, edges=edges)
    g.vs["id"] = [ x.id for x in nodes ]
    g.vs["label"] = [ x.label for x in nodes ]
    g.es["length"] = [ x.length for x in nodes[1:] ]
    return g
