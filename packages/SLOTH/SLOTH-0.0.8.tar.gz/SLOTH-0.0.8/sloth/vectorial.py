# -*- coding: utf-8 -*-
#  This file is part of SLOTH - stick/like object tracking in high-resolution.
#    Copyright (C) 2012 Monika Kauer
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#@author: Monika Kauer

import math
#==============================================================================
# Vector class with neat methods
#==============================================================================
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __str__(self):
        return "(%s, %s)"%(self.x, self.y)
    def __repr_(self):
        return "vec(%s, %s)"%(self.x, self.y)
    def __add__(self, v):
        return Vector(self.x+v.x, self.y+v.y)
    def __sub__(self, v):
        return Vector(self.x-v.x, self.y-v.y)
    def __abs__(self):
        return (self.x**2+self.y**2)**0.5
    def __mul__(self, n):
        return Vector(self.x*n, self.y*n)
    def __div__(self, n):
        if n!=0:
            return Vector(self.x/n, self.y/n)
        else:
            return self
    def __neg__(self):
        return Vector(-self.x, -self.y)
    def normalize(self):
        return self/abs(self)
    def rotate(self, a):
        sina = math.sin(math.pi*a/180.0)
        cosa = math.cos(math.pi*a/180.0)
        return Vector(cosa*self.x -sina*self.y, sina*self.x + cosa*self.y)
