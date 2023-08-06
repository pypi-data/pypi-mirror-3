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

from scipy import optimize, ndimage
import numpy as np
import array
import vectorial
import image_processing as ip

def new_object(objects, hints, y, xmin, xmax):
    "add a new horizontal line segment as new object and merge with old objects"
    v = (y, xmin, xmax)
    objectnr = None
    for nr in hints.get(y-1, []):
        items = objects.get(nr, [])
        for i in range(len(items)-1, -1, -1):
            if items[i][0] < (y - 1):  break
            if items[i][0] == y:       continue
            assert items[i][0] == y - 1
            if max(xmin, items[i][1]) <= min(xmax, items[i][2]):
                if not objectnr:
                    objectnr = nr
                else:
                    objects[objectnr] = list(set(objects[objectnr]).union(items))
                    objects[objectnr].sort()
                    del objects[nr]
                break
    if objectnr:
        objects[objectnr].append(v)
    else:
        objectnr = (y<<16)+xmin
        assert objectnr not in objects
        objects[objectnr] = [v]
    hints.setdefault(y, set())
    hints[y].add(objectnr)


def detect_objects(image, width, height, parameter):
    "detect objects line by line by checking for a certain limit"
    image =  array.array("H", image.tostring())
    maximum   = max(image)
    minimum   = min(image)
    objects   = {}
    hints     = {}
    prev = False
    diff = (maximum-minimum) * parameter
    for i in range(height*width):
        if i % width == 0:
            avg = image[i]
        elif not prev:
            avg = avg*0.95 + image[i]*0.05
        value = image[i]
        v = (value-avg) > diff
        if v != prev:
            if not v:
                end = i - 1
                y = end/width
                while start/width != y:
                    new_object(objects, hints, start/width, start % width, width-1)
                    start += width - (start % width)
                new_object(objects, hints, y, start % width, end%width)
            prev = v
            start = i
    return objects

def draw_line(image, color, x1, y1, x2, y2):
    "simple bresenham"
    deltax, deltay =  abs(x2 - x1), -abs(y2 - y1)
    err = deltax + deltay
    while True:
        image[y1][x1] = color
        if x1 == x2 and y1 == y2:
            break
        e = 2*err
        if e > deltay:
            err += deltay
            x1 += x1 < x2 and 1 or -1
        if e < deltax:
            err += deltax
            y1 += y1 < y2 and 1 or -1

def fit_direction(image, objects):
    """takes an object(group of pixels in an image) and finds a major axis by linear least squares fit with pixel intensity weights."""
    for nr in objects:
        o = objects[nr]
        xlist = []
        ylist = []
        intensity = []
        for v in o:
            for x in range(v[1], v[2]+1):
                xlist.append(x)
                ylist.append(v[0])
                intens = image[v[0]][x]
                intensity.append(1+intens)       
        if len(xlist) < 20:
            continue
        cms=(0,np.average(xlist),np.average(ylist))
        xlist = np.array(xlist)
        ylist = np.array(ylist)
        intensity = np.array(intensity)
        fitfunc = lambda p, a: p[0] * a + p[1]
        errfunc = lambda p, a, b, i: (fitfunc(p, a) - b) / (i*i)
        p1,cov,infodict,mesg,ier = optimize.leastsq(errfunc, (1, 1), args=(xlist, ylist, intensity),full_output=True)
        yield cms, p1

def calculate_coordinates(midpoint, p1, test_len):
    """transfers output to real coordinates"""
    betr=(p1[0]**2+1)**0.5
    direction=(test_len/betr,test_len/betr*p1[0])
    x=midpoint[1]+direction[0]
    y=midpoint[2]+direction[1]
    dx=-direction[0]*2
    dy=-direction[1]*2
    return vectorial.Vector(x,y),vectorial.Vector(dx,dy)

import array
def FindOptimalDirections(first_image,seed_coordinates,width,options):
    """elongates an object by options["STEP LENGTH"] if this gains enough intensity."""
    linear_image = array.array("H", first_image.tostring())
    for start, direction in seed_coordinates:
        #steps to elongate MT, if this yields enough intensity
        maxstart=start
        maxdir=direction
        negdir = (-direction*options["STEP LENGTH"])/options["LENGTH PROTOTYPE"]
        posdir = -negdir
        maxintensity = ip.vec_intensity2(linear_image, width, start, direction) * options["ELONGATION"]*options["STEP LENGTH"]
        try:
            while ip.vec_intensity2(linear_image,width,maxstart,negdir) > maxintensity:
                maxstart += negdir          
                maxdir += posdir
                end = start + maxdir
                while ip.vec_intensity2(linear_image,width,end,posdir) > maxintensity:
                    end += posdir
                    maxdir += posdir
            midpoint=maxstart+maxdir*0.5
            yield [maxstart, maxdir, midpoint]
        except IndexError:
            print 'FindOptimalDirections filtered', (y,x)    
        
         
