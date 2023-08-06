# -*- coding: utf-8 -*-
#Created on Mon Jun 25 15:11:07 2012
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


import image_processing as ip
import vectorial
import numpy as np
import array

def FineTuneCoordinates(first_image, seed_coordinates, options):
    """takes list of coordinates,an image and a length scan option to determine the exact tip using a fit function."""
    for start,direction,midpoint in seed_coordinates:
        LENGTH=abs(direction)
        width=first_image.shape[0]
        height=first_image.shape[1]
        try:
            tip_r,_,_=FermiFitTipPositions(first_image, midpoint, -direction, len_scan=LENGTH*options["SCAN LENGTH FACTOR"])
            tip_l,_,_=FermiFitTipPositions(first_image, midpoint, direction,len_scan=LENGTH*options["SCAN LENGTH FACTOR"])
            if tip_r.x>width or tip_r.y>height or tip_l.x>width or tip_l.y>height:
                continue
            if (abs(tip_r-tip_l)>options["MINIMAL LENGTH"] and ip.vec_intensity(first_image,tip_r, tip_l-tip_r)/abs(tip_r-tip_l)>options["MIN INTENSITY"]):
                yield [tip_r, tip_l-tip_r, tip_r+(tip_l-tip_r)*0.5]
            else:
                print "Intensity too low for", midpoint
        except IndexError:
            print 'FineTuneCoordinates filtered (%d,%d)'%(midpoint.x, midpoint.y)
            
            
def FindNewTip(image, objects, d, last_len, options):
    """calculate a new tip from the objects coordinates, given as (start,direction,midpoint)=objects.
    """
    linear_image = array.array("H", image.tostring())
    start,direction,midpoint = objects
    try:
        current_length=abs(direction)
        #drift correct the reference points
        start1=start+d
        midpoint1=midpoint+d
        end1=start1+direction
        
        old_intensity=ip.vec_intensity2(linear_image,image.shape[0], start1,direction)/current_length
        #rotate, if the extension has a direction different from the seed
        direction_test=direction.normalize()*options["TEST LENGTH"]
        #calculate rotating intensity
        
        if options["BENDING ANGLE"]!=0:
            maxstart,negdir,maxv1=RotatingIntensity(image,linear_image,start1,-direction_test,alpha_min=-options["BENDING ANGLE"], alpha_max=options["BENDING ANGLE"], step=360/3/options["TEST LENGTH"],center=False)
            end,posdir,maxv2=RotatingIntensity(image,linear_image,start1+direction,direction_test,alpha_min=-options["BENDING ANGLE"], alpha_max=options["BENDING ANGLE"], step=360/3/options["TEST LENGTH"],center=False)
            
        if maxv1>options["END BENDING THRESHOLD"]*old_intensity:
            len_scan=last_len[0]+options["TEST LENGTH"]
            tip1,slope1,params1=FermiFitTipPositions(image,maxstart,negdir,len_scan)
            if slope1 > 0:
                tip1,slope1,params1=FermiFitTipPositions(image,midpoint1,-direction,current_length*options["SCAN LENGTH FACTOR"])
            err1=0.5/params1[1]/3.
            l_plus=abs(midpoint1-start1)+abs(start1-tip1)

        elif maxv1<options["END BENDING THRESHOLD"]*old_intensity:
            len_scan=current_length*options["SCAN LENGTH FACTOR"]
            tip1,slope1,params1=FermiFitTipPositions(image,midpoint1,-direction,len_scan)
            err1=0.5/params1[1]/3.
            l_plus=tip1-midpoint1

        if maxv2>options["END BENDING THRESHOLD"]*old_intensity:
            len_scan=last_len[1]+options["TEST LENGTH"]
            tip2,slope2,params2=FermiFitTipPositions(image,end,posdir,len_scan)
            if slope2 > 0:#for better catastrophe handling
                tip2,slope2,params2=FermiFitTipPositions(image,midpoint1,direction,current_length*options["SCAN LENGTH FACTOR"])
            err2=0.5/params2[1]/3.
            l_minus=abs(midpoint1-end)+abs(end-tip2)
            
        elif maxv2<options["END BENDING THRESHOLD"]*old_intensity:
            len_scan=current_length*options["SCAN LENGTH FACTOR"]
            tip2,slope2,params2=FermiFitTipPositions(image,midpoint1,direction,len_scan)
            err2=0.5/params2[1]/3.
            l_minus=midpoint1-tip2

        return (abs(l_plus), abs(l_minus)), tip1.x,tip1.y,tip2.x,tip2.y, abs(l_plus),abs(l_minus), slope1,slope2, old_intensity, abs(err1), abs(err2), params1[0], params1[3], params2[0], params2[3]
    except IndexError, ValueError:
        return ((10, 10),)

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
            v = ip.vec_intensity2(linear_image, image.shape[1], start, direction2)/l
            if v > maxv:
                maxv = v
                maxdir = direction2
                maxstart = start
        except IndexError:
            pass
    return maxstart,maxdir,maxv        
        
def FermiFitTipPositions(image, start_scan, direction, len_scan):
    """Fit Fermi-function to data and find x_fwhm for tip position"""
    l=abs(direction)
    linear_image = array.array("H", image.tostring())
    width=image.shape[0]
    profile=ip.end_profile2(linear_image,width,start_scan,direction/l, len_scan)  
    profile=np.array(profile, dtype="float64")
    params,r_square,fit,x_fwhm,y,slope=ip.error_fit(profile,[max(profile),0.8,4.0,min(profile)])
#    pylab.figure()
#    pylab.plot(profile,'r.')
#    pylab.hold(True)
#    pylab.plot(fit,'b:')
#    pylab.plot(x_fwhm,y,'o')
    #calculate actual tip positions from fit.
    tip=start_scan+direction.normalize()*x_fwhm
    return tip,slope,params
    
