"""
Convenience functions for drawing shapes on TreePlots.
"""
import Image
from numpy import sin, cos, linspace, pi, degrees, sqrt
from matplotlib.collections import RegularPolyCollection
from matplotlib.transforms import offset_copy
from matplotlib.patches import Rectangle, Wedge
from matplotlib.offsetbox import DrawingArea
try:
    from matplotlib.offsetbox import OffsetImage, AnnotationBbox
except ImportError:
    pass
from ..tree import Node
import colors as _colors

def _xy(plot, p):
    if isinstance(p, Node):
        c = plot.n2c[p]
        p = (c.x, c.y)
    elif isinstance(p, (list, tuple)):
        p = [ _xy(plot, x) for x in p ]
    else:
        pass
    return p

def image(plot, p, imgfile,
          maxdim=100, border=0,
          xoff=4, yoff=4,
          halign=0.0, valign=0.5,
          xycoords='data', boxcoords=('offset points')):
    if xycoords == "label":
        xycoords = plot.node2label[p]
        x, y = (1, 0.5)
    else:
        x, y = _xy(plot, p)
    img = Image.open(imgfile)
    if max(img.size) > maxdim:
        img.thumbnail((maxdim, maxdim))
    imgbox = OffsetImage(img)
    abox = AnnotationBbox(imgbox, (x, y),
                          xybox=(xoff, yoff),
                          xycoords=xycoords,
                          box_alignment=(halign,valign),
                          pad=0.0,
                          boxcoords=boxcoords)
    plot.add_artist(abox)
    plot.figure.canvas.draw_idle()

def images(plot, p, imgfiles,
          maxdim=100, border=0,
          xoff=4, yoff=4,
          halign=0.0, valign=0.5,
          xycoords='data', boxcoords=('offset points')):
    for x, f in zip(p, imgfiles):
        image(plot, x, f, maxdim, border, xoff, yoff, halign, valign,
              xycoords, boxcoords)

def pie(plot, p, values, colors=None, size=16, norm=True,
        xoff=0, yoff=0,
        halign=0.5, valign=0.5,
        xycoords='data', boxcoords=('offset points')):
    x, y = _xy(plot, p)
    da = DrawingArea(size, size); r = size*0.5; center = (r,r)
    x0 = 0
    S = 360.0
    if norm: S = 360.0/sum(values)
    if not colors:
        c = _colors.tango()
        colors = [ c.next() for v in values ]
    for i, v in enumerate(values):
        theta = v*S
        if v: da.add_artist(Wedge(center, r, x0, x0+theta,
                                  fc=colors[i], ec='none'))
        x0 += theta
    box = AnnotationBbox(da, (x,y), pad=0, frameon=False,
                         xybox=(xoff, yoff),
                         xycoords=xycoords,
                         box_alignment=(halign,valign),
                         boxcoords=boxcoords)
    plot.add_artist(box)
    plot.figure.canvas.draw_idle()
    

def hbar(plot, p, values, colors=None, height=16,
         xoff=0, yoff=0,
         halign=1, valign=0.5,
         xycoords='data', boxcoords=('offset points')):
    x, y = _xy(plot, p)
    h = height; w = sum(values) * height#; yoff=h*0.5
    da = DrawingArea(w, h)
    x0 = -sum(values)
    if not colors:
        c = _colors.tango()
        colors = [ c.next() for v in values ]
    for i, v in enumerate(values):
        if v: da.add_artist(Rectangle((x0,0), v*h, h, fc=colors[i], ec='none'))
        x0 += v*h
    box = AnnotationBbox(da, (x,y), pad=0, frameon=False,
                         xybox=(xoff, yoff),
                         xycoords=xycoords,
                         box_alignment=(halign,valign),
                         boxcoords=boxcoords)
    plot.add_artist(box)
    plot.figure.canvas.draw_idle()

def hbars(plot, p, values, colors=None, height=16,
          xoff=0, yoff=0,
          halign=1, valign=0.5,
          xycoords='data', boxcoords=('offset points')):
    for x, v in zip(p, values):
        hbar(plot, x, v, colors, height, xoff, yoff, halign, valign,
             xycoords, boxcoords)

def squares(plot, p, colors, size=15, xoff=0, yoff=0):
    points = _xy(plot, p)
    trans = offset_copy(
        plot.transData, fig=plot.figure, x=xoff, y=yoff, units='points'
        )

    col = RegularPolyCollection(
        numsides=4, rotation=pi*0.25, sizes=(size*size,),
        offsets=points, facecolors=colors, transOffset=trans,
        edgecolors='none'
        )

    plot.add_collection(col)
    plot.figure.canvas.draw_idle()

def circles(plot, p, colors, size=15, xoff=0, yoff=0):
    points = _xy(plot, p)
    trans = offset_copy(
        plot.transData, fig=plot.figure, x=xoff, y=yoff, units='points'
        )

    col = CircleCollection(
        sizes=(pi*size*size*0.25,),
        offsets=points, facecolors=colors, transOffset=trans,
        edgecolors='none'
        )

    plot.add_collection(col)
    plot.figure.canvas.draw_idle()
