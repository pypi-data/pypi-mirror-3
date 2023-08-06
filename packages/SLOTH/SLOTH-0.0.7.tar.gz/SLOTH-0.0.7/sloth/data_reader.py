# -*- coding: utf-8 -*-
#Created on Mon Jun 25 17:48:25 2012
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
import pylab
import csv
import operator

class Data_Reader:
    "reader object for image analyser output"
    def __init__(self, filename):
        f=open(filename)
        f.next()
        f.next()
        reader=csv.reader(f, delimiter=" ", quoting=csv.QUOTE_NONNUMERIC)
        self.data=sorted(reader, key=operator.itemgetter(0), reverse=False)
        self.max=max(map(lambda x: int(x[0]),self.data))
    
    def get_object(self, number):
        data=[]
        dat=[]
        for k in self.data:
            if int(k[0])==number:
                data.append(k)
        data.sort()
        return data
        

        
def read_data(generator, columns):
    '''reads the columns specified as [] from data.'''
    output=	[]
    for dat in generator:
        helper=[]
        for number in columns:
            helper.append(dat[number])
        output.append(helper)
    output=np.transpose(output)
    return output

           
def speed_filter(data, max_speed, framerate, pixelsize):
    '''data is a list of data eg. [length, errors]^T, at position 0 needs to be the length.'''
    i=0
    filtered=[]
    while i<(len(data)-1):
        try:
            if abs(data[i+1][0]-data[i][0])*pixelsize*60>max_speed*framerate:
                k=1
                while(abs(data[i+k][0]-data[i][0])*pixelsize*60>k*max_speed*framerate):
                    k+=1
                i+=k
            else:
                filtered.append(data[i].tolist()) 
                i+=1
        except IndexError:
            break
    if len(filtered)==0:
        return [[]]*len(data[0])        
    return filtered

def error_filter(data, max_displacement, pixelsize):
    '''data is a list of data eg. [length, errors]^T, at position 0 needs to be the length.'''
    filtered=[]
    for i in range(len(data)):
        if data[i][1]*pixelsize<max_displacement:
            filtered.append(data[i])
    if len(filtered)==0:
        return np.transpose([[]]*len(data[0]))       
    return filtered
