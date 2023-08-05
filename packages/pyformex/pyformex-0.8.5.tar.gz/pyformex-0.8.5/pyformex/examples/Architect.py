#!/usr/bin/pyformex --gui
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

"""Architect

level = 'normal'
topics = ['']
techniques = ['Hex8']

"""
reset()
smooth()

class Wall(Formex):
    """A Formex representing a wall.

    A Wall is a hexahedral part defined by eight vertices. The edges are
    always straight lines. The borders of the hexahedron are usually flat
    planes and opposite planes are most often parallel, though this is not
    a requirement.
    Furthermore, the Wall can contain any number of hexahedral holes.
    """
    all = []
    
    def __init__(self,coords):
        """Construct a new Wall."""
        Formex.__init__(self,coords,eltype='hex8')
        if self.shape() != (1,8,3):
            raise ValueError,"Expected an (8,3) shaped Coords or Formex"

        Wall.all.append(self)


class Wall_defaults(object):
    thickness=140
    


def createWall(p0,p1,h,t=Wall_defaults.thickness):
    F = Formex([[p0,p1]],prop=7).extrude(1,h,dir=2).extrude(1,t,dir=0)
    return Wall(F)

def createWall_1(p0,p1,h0,h1,t=Wall_defaults.thickness):
    X0 = Coords(p0)
    X1 = Coords(p1)
    F = Formex([[X0,X1,X1.trl(2,h1),X0.trl(2,h0)]],prop=6).extrude(1,t,dir=0)
    return Wall(F)


L = 10000.
B = 8000.
h0 = 2600.
h1 = 5200.
h2 = 8000.
Ba = 3500.
Bb = B - Ba
BA = 5500.
BB = B - BA

WL = createWall([0,0],[0,L],h0)
WL = createWall([B,0],[B,L],h1)
Wa = createWall_1([0,0],[Ba,0],h0,h2)
Wb = createWall_1([Ba,0],[B,0],h2,h1)

draw(Wall.all)


# End
