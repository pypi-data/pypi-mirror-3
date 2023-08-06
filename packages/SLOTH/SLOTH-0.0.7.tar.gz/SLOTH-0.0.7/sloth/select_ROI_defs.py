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
from sloth import image_processing as ip
from sloth import vectorial
from sloth import data_reader
from sloth import image_analyser_defs as iad
import pylab
import array
import numpy as np
from scipy import stats, sqrt

def show_movie(filename,fps=0.1, start=0):
    """dispays nd2 movie from start to end"""
    image_file=ip.MyImageFile(filename, dual_color=True)
    image = image_file.get_frame(0)
    f=pylab.figure()
    pylab.ion()
    end=image_file.number_frames
    m=pylab.imshow(image,interpolation='nearest', cmap="gray")
    pylab.draw()
    for frame in range(start, end):
        image = image_file.get_frame(frame)
        m.set_data(image)
        pylab.draw()
        f.canvas.flush_events()
        print frame
        #time.sleep(1)


def make_kymo(data,filename_movie, framerate, twocolor):
    """produces a kymograph from tip data and movie"""
    image_file=ip.MyImageFile(filename_movie, dual_color=twocolor)
    tip1x=data[0]
    tip1y=data[1]
    tip2x=data[2]
    tip2y=data[3]
    length1=data[4]
    length2=data[5]
    kymo=[]
    if tip1x==[] or tip2x==[] or tip1y==[] or tip2y==[]:
        return 0,0,[],[]
    l1max=int(max(length1)) #calculate maximal length
    l2max=int(max(length2))
    shift=20 #how far is MT from borders
    midpoint=(vectorial.Vector(tip1x[0],tip1y[0])+vectorial.Vector(tip2x[0],tip2y[0]))*0.5
    l0=abs(vectorial.Vector(tip1x[0],tip1y[0])-vectorial.Vector(tip2x[0],tip2y[0]))
    for frame in range(0,max([len(length1),len(length2)])):
        image = image_file.get_frame(frame)
        linear_image = array.array("H", image.tostring())
        direction1=vectorial.Vector(tip1x[frame],tip1y[frame])-midpoint
        profile1=ip.end_profile2(linear_image,image.shape[0],midpoint,direction1.normalize(),l1max+shift)
        direction2=vectorial.Vector(tip2x[frame],tip2y[frame])-midpoint
        profile2=ip.end_profile2(linear_image,image.shape[0],midpoint,direction2.normalize(),l2max+shift+int(l0/2))
        profile=profile1[::-1]+profile2
        kymo.append(profile)
    #post processing to get it to image format
    if len(kymo)>0:
        pylab.imshow(kymo, cmap="gray", interpolation="nearest")
        len1=map(lambda x: -x+shift+l1max,length1)
        len2=map(lambda x: x+shift+l1max,length2)
        pylab.hold(True)
        pylab.plot(len1,range(len(length1)),'-', color='red')
        pylab.plot(len2,range(len(length2)),'-', color='blue')    
    
def growth_speed(length1,framerate, linreg=False, start=0, end=10000, output=True):
    '''input is length data as read in read data. performs linear least-squares fit. output=False suppresses plotting.'''
    fit1=[]
    a_1=0
    stderr1=0
    #create time in ms
    time1=np.arange(0,len(length1)*framerate,framerate)
    
    if start or end:
        time1=time1[start:end]
        length1=length1[start:end]

    if linreg:
        (a_1,b_1,r1,p1,stderr1)=stats.linregress(time1,length1)
        #correct standard error, wrong definition in stats package
        stderr1=sqrt(1./(len(time1)-2)*a_1**2*(1-r1**2)/r1**2)
        
        print(' growth velocity length1: %.2f +-%.2f um/min  \n ' % (a_1*60,stderr1*60))
        for i in time1:
            fit1.append(a_1*i+b_1)
    if output:
        fig=pylab.figure(103,figsize=(8,5))
        pylab.ion()
        pylab.plot(time1/framerate,length1,'-', label='length1')
        if linreg:
            pylab.plot(time1/framerate,fit1)    
        #pylab.legend()
        pylab.xlabel('index of data')
        pylab.ylabel('length in nm')
        pylab.title('Current velocity: %.2f +- %.2f um/min'%(a_1*60,stderr1*60))
        pylab.draw()
        fig.canvas.flush_events()
    #this is velocity in um/min
    a_1=a_1*60
    stderr1=stderr1*60
    return a_1,stderr1
