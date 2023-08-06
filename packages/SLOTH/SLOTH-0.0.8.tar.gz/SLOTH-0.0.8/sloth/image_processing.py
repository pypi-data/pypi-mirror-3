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

import numpy as np
import vectorial
from scipy import optimize
import matplotlib.pylab as pylab
import array

#==============================================================================
# Class to abstract from file formats
#==============================================================================
class MyImageFile:
    "Abstracts from file format like nd2 or tiff"
    def __init__(self, filename, dual_color, shift=1):
        if filename.endswith(".nd2"):
            import read_nd2
            self.raw_image = read_nd2.Nd2File(open(filename))
            self.dual_color = dual_color
            self.number_frames=self.raw_image.attr["uiSequenceCount"]
            self.shape=(self.raw_image.attr['uiHeight'],self.raw_image.attr['uiWidth'])
            self.fmt="nd2"
            self.shift=shift
        elif filename.lower().endswith(".tif"):
            import tifffile
            self.raw_image = tifffile.TIFFfile(filename)
            self.number_frames = len(self.raw_image)-1
            self.shape = self.raw_image[0].asarray().shape
            self.fmt = "tif"
            self.shift=0
        else:
            raise Exception("unkown filetype %s"%filename)

    def get_frame(self, number):
        """returns frame(number) of a MyImageFile object"""
        if self.fmt=="nd2":
            frame =  self.raw_image.get_image(number)
            red=np.ndarray(self.shape,dtype="H", buffer=frame[1])
            if not self.dual_color:
                return red
            green=np.ndarray(self.shape, dtype='H', buffer=frame[2])
            return red + green*int(self.shift)
        if self.fmt=="tif":
            return self.raw_image[number].asarray()

#========================================================t======================
# Major functions of tracking program
#==============================================================================

def vec_intensity(image, pos, direction):
    """calculates the total intensity along a line, where pos=starting point in the direction given. pos and direction are sloth.vectorial.Vector objects."""
    intensity=0.0
    l = abs(direction)
    for j in range(int(l)):
        newp = pos + (direction/l)*j
        intensity += image[int(round(newp.y))][int(round(newp.x))]
    return intensity

def vec_intensity2(linear_image, width, pos, direction):
    """faster intensity calculation"""
    l=abs(direction)
    return sum(end_profile2(linear_image,width, pos, direction/l, l))
#==============================================================================
#  Fitting routines for Fermi-Tip # XXX get better initial values
#==============================================================================

# Fits Fermi Function to Tip profile and returns Fit params and Coord at Half Maximum
#==============================================================================   
def error_fit(profile,p0):
    """least square fit to a fermi function:\n
    p[0]*(1./(np.exp(a*p[1]-p[2])+1))+p[3]
     Returns parameters, r^2, fit, the position of the half-maximum and the slope at the half-maximum."""
    coords=np.array(range(len(profile)))
    profile=np.array(profile)
    #Fit to Fermifunction
    fitfunc = lambda p, a: p[0]*(1./(np.exp(a*p[1]-p[2])+1))+p[3] # Target function
    errfunc = lambda p, a, b: (fitfunc(p, a)-b)# Distance to the target 
    p1,cov,infodict,mesg,ier = optimize.leastsq(errfunc, p0[:], args=(coords, profile),full_output=True)#least square fit
    ss_err=(infodict['fvec']**2).sum()
    ss_tot=((profile-profile.mean())**2).sum()
    rsquared=1-(ss_err/ss_tot)
    fit = fitfunc(p1, np.array(coords))
    #pylab.figure(8)
    #pylab.hold(True)
    #pylab.plot(profile,'k.',fit,'-', color='#0B2A51')
    #Find Half Maximum
    y=max(fit)-(max(fit)-min(fit))/2.
    if p1[0]/(y-p1[3])-1.>0:
        x_fwhm=(np.log(p1[0]/(y-p1[3])-1.)+p1[2])/p1[1]
    else:
        x_fwhm=0
    slope=-p1[1]/p1[0]*(p1[0]-y+p1[3])*(y-p1[3])
    #pylab.plot(x_fwhm,y,"kx", markersize=10)
    #pylab.hold(False)
    if np.isinf(x_fwhm) or np.iscomplex(x_fwhm) or np.isnan(x_fwhm):
        return p1,rsquared,fit,0,y,slope
    else: 
        return p1,rsquared,fit, x_fwhm,y,slope
 
        
#==============================================================================
#     Display Functions
#==============================================================================

def ShowCoordinates(image, directions):
    "Plot coordinates ontop of image with matplotlib."
    fig=pylab.imshow(image, cmap="gray")
    for i in range(len(directions)):
        k = directions[i]
        end = k[0] + k[1]
        mp = k[0] + k[1]*0.5
        pylab.hold(True)
        pylab.plot(k[0].x,k[0].y,'r+')
        pylab.plot(end.x,end.y,'r*')
        pylab.text(mp.x,mp.y, '%d' %i, color="w")
    pylab.hold(False)


def RotatingIntensity(image, linear_image, axis,direction,alpha_min, alpha_max, step, center=True):
    '''Rotate microtubule to maximum intensity.
    If center is False, the rotation axis is the start point.'''
    maxv = 0
    maxstart=None
    maxdir=None
    l=abs(direction)
    for alpha in np.arange(alpha_min,alpha_max,step):
        direction2=direction.rotate(alpha)
        if center:
            start = axis + direction2 * -0.5 
        else:
            start = axis
        try:
            v = vec_intensity2(linear_image, image.shape[1], start, direction2)/l
            if v > maxv:
                maxv = v
                maxdir = direction2
                maxstart = start
        except IndexError:
            pass
    return maxstart,maxdir,maxv


def end_profile(image, start, direction):
    "Go through image from one endpoint, and record intensity profile."
    pos = start + direction
    try:
        i = image[int(round(pos.y))][int(round(pos.x))]
    except IndexError:
        i = 0
    return i, pos

def end_profile2(linear_image,width, start, direction, len_scan):
    """Go through image from one endpoint, and record intensity profile.
    Uses linearized array, therefore faster.
    """
    intensity=[]
    for j in range(int(np.ceil(len_scan))):
        newp = start + (direction)*j
        try:           
            intensity.append(linear_image[int(round(newp.y))*width + int(round(newp.x))])
        except IndexError:
            intensity.append(0)
    return intensity

def tracker_data(filename):
    """reads position data (x,y) in file. Data needs to be separated by tab."""
    pos=list()
    length=list()
    if filename==None or len(filename)==0:
        return None
       
    with open(filename, 'r') as f:
        dialect = csv.Sniffer().sniff(f.read(1024))
        f.seek(0)
        data=csv.reader(f,dialect)
        for k in data:
            pos.append([float(k[0]),float(k[1])])
    return pos
