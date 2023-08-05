#!/usr/bin/env pyformex --gui
# $Id: FontForge.py 162 2011-09-23 09:27:10Z bene $
##
##  This file is part of pyFormex 0.8.5  (Sun Dec  4 21:24:46 CET 2011)
##  pyFormex is a tool for generating, manipulating and transforming 3D
##  geometrical models by sequences of mathematical operations.
##  Home page: http://pyformex.org
##  Project page:  http://savannah.nongnu.org/projects/pyformex/
##  Copyright 2004-2011 (C) Benedict Verhegghe (benedict.verhegghe@ugent.be) 
##  Distributed under the GNU General Public License version 3 or later.
##
##
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License
##  along with this program.  If not, see http://www.gnu.org/licenses/.
##
"""FontForge

Demonstrates the use of FontForge library to render text.
"""
from pyformex import odict,PF
from plugins.curve import BezierSpline
from simple import connectCurves

from gui import widgets

f = widgets.selectFont()
print f
print dir(f)
#exit()


def BezierSplit():

    def parts(self,j,k):
        """Return a curve containing only parts j to k."""
        start = self.degree * j
        end = self.degree * k + 1
        return BezierSpline(control=self.coords[start:end],degree=self.degree,closed=False)

    def split(self,split):
        """Split a curve into a list of partial curves

        split is a list of integer values specifying the node numbers
        where the curve is to be split.
        """
        start = [0] + split
        end = split + [-1]
        return [ self.parts(j,k) for j,k in zip(start,end) ]
        
    BezierSpline.split = split
    BezierSpline.parts = parts

BezierSplit()    

fonts = odict.ODict([
    ('blippo',"/mnt/work/local/share/fonts/blippok.ttf"),
    ('blimpo',"/home/bene/tmp/Blimpo-Regular.ttf"),
    ('verdana',"/var/lib/defoma/x-ttcidfont-conf.d/dirs/TrueType/Verdana.ttf"),
    ])

flat()

try:
    import fontforge
except ImportError:
    warning("I could not import 'fontforge'.\nYou probably do not have 'fontforge' and/or its Python bindings installed on this machine.\nPlease install 'fontforge' and 'python-fontforge' and then try again.")
    exit()

print dir(fontforge)

from PyQt4.QtGui import QDesktopServices as QD
print QD.storageLocation(QD.FontsLocation)

exit()  

def glyphCurve(c):
    """Convert a glyph contour to a list of quad bezier curves."""
    points = []
    control = []
    P0 = c[0]
    points.append([P0.x,P0.y])
    for i in (arange(len(c))+1) % len(c):
        P = c[i]
        if P0.on_curve and P.on_curve:
            # straight segment
            control.append([0.5*(P0.x+P.x),0.5*(P0.y+P.y)])
            points.append([P.x,P.y])
            P0 = P
            continue
        elif P0.on_curve and not P.on_curve:
            # undecided
            P1 = P0
            P0 = P
            continue
        elif not P0.on_curve and P.on_curve:
            # a single quadratic segment
            control.append([P0.x,P0.y])
            points.append([P.x,P.y])
            P0 = P
            continue
        else: # not P0.on_curve and not P.on_curve:
            # two quadratic segments, central point to be interpolated
            PM = fontforge.point()
            PM.x = 0.5*(P0.x+P.x)
            PM.y = 0.5*(P0.y+P.y)
            PM.on_curve = True
            points.append([PM.x,PM.y])
            control.append([P0.x,P0.y])
            P1 = PM
            P0 = P
            continue
    
    return Coords(points),Coords(control)


def charContour(fontname,character):
    fontfile = fonts[fontname]
    font = fontforge.open(fontfile,5)
    print "FONT INFO FOR %s" % font
    print dir(font)
    print font.gpos_lookups

    g = font[ord(character)]
    print "GLYPH INFO FOR %s" % g
    print dir(g)
    print g.getPosSub


    l = g.layers[1]
    print len(l)
    c = l[0]
    print c
    print dir(c)
    print c.closed
    print c.is_quadratic
    print c.isClockwise()
    print len(c)
    print c.reverseDirection()

    if c.isClockwise():
        c = c.reverseDirection()

    return c
    
            
def charCurve(fontname,character):
    c = charContour(fontname,character)
    points,control = glyphCurve(c)
    curve =  BezierSpline(coords=points[:-1],control=control,degree=2,closed=True)
    export({'%s-%s'%(fontname,character):curve})
    return curve


def drawCurve(curve,color,with_points=True):
    draw(curve,color=color)
    if with_points:
        drawNumbers(curve.pointsOn())
        drawNumbers(curve.pointsOff(),color=red)


if PF.has_key('__FontForge__data__'):
    globals().update(PF['__FontForge__data__'])
else:
    fontname1 = fontname2 = 'blippo'
    character1 = character2 = 'p'

1
res = askItems([
    ('fontname1',fontname1,'select',{'choices':fonts.keys()}),
    ('character1',character1,{'max':1}),
    ('fontname2',fontname2,'select',{'choices':fonts.keys()}),
    ('character2',character2,{'max':1}),
    ])

if not res:
    exit()
    
globals().update(res)
if not character:
    exit()

export({'__FontForge__data__':res})


curve1 = charCurve(fontname1,character1)
curve2 = charCurve(fontname2,character2)

size = curve1.pointsOn().bbox().dsize()
curve2.coords = curve2.coords.trl([0.,0.,size])
clear()

drawCurve(curve1,blue)

curve3 = curve1.parts(0,2)
drawCurve(curve3,red)
exit()

print curve1.nparts
fwd = array([ curve1.sub_directions(0.0,i)[0] for i in range(curve1.nparts) ])
bwd = array([ curve1.sub_directions(1.0,i)[0] for i in range(curve1.nparts) ])
print fwd[1:]
print bwd[:-1]

disc = fwd[1:] - bwd[:-1]
print disc

corners = where(length(disc) > 0.1)[0] + 1

subcurves = curve1.partition(corners)



exit()
drawCurve(curve2,red)
exit()
print curve1.nparts
print curve2.nparts

## G = Formex(pattern('1234'))
## draw(G)
## exit()
F0 = curve1.toFormex()
F1 = curve2.toFormex()

F = connectCurves(F0,F1,4)
draw(F,color=black)



# End
