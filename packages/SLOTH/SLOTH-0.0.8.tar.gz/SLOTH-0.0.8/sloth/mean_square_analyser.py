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
from scipy import stats, sqrt, arange, optimize
import matplotlib.pylab as pylab
import math

#==============================================================================
#  Mean-square  methods
#==============================================================================
  
def welch_test(x,y,semx,semy,dofx,dofy):
    """returns t and dof for welchs unpaired t test"""
    return abs(x-y)/(sqrt(semx**2+semy**2)), (semx**2+semy**2)**2/(semx**4/dofx+semy**4/dofy)
    
def tracker_data_2(workingDir):
    """reads and averages coordinates in folder"""
    bead_pos=[]
    for datei in os.listdir(workingDir):
        raw_data=[]
        with open(workingDir+"/"+datei) as file:
            a=csv.reader(file, delimiter=" ")
            #a.next()#skip header
            for row in a:    
                raw_data.append([float(row[0]),float(row[1])])
        bead_pos.append(raw_data)
    bead_pos=np.transpose(bead_pos)
    f= open(workingDir+"/../%s_drift"%(datei.split("-")[0]),'wa')
    x=[]
    y=[]
    for j in range(len(bead_pos[0])):
            x.append(np.average(bead_pos[0][j]))
            y.append(np.average(bead_pos[1][j]))
            f.write('%f %f \n'%(np.average(bead_pos[0][j]),np.average(bead_pos[1][j])))
    f.close()       
    return [x,y]
                
def msq_from_data_lsq(length,dt,p0):
    """calculates mean square displacement values for a series of lengths. Time intervals are taken as powers of 2 to avoid correlations."""
    #calculate mean -square displacement
    msq=list()
    tau=[]
    i=1
    #log distance to reduce correlations.
    nmax=np.log2(len(length)/2.)
    for a in range(0,int(np.floor(nmax))):
           tau.append(i*2)
           i=i*2
    avg=[]
    weights=[]
    print tau
    for t in tau:
        msq=[]
        for i in range(0,len(length)-t,t+1):
            msq.append((length[i]-length[i+t])**2)  
        msq=[k for k in msq if np.isnan(k)!=True]
        if len(msq)>1:
            avg.append(np.average(msq)) 
            weights.append(np.std(msq, ddof=1)/sqrt(len(msq)))
    tau=map(lambda x: x*dt, tau)        
    p,fit,pcov,info=lq_diffusion_fit_constrained(tau,avg,weights,p0)
    s2=sum(info['fvec']*info['fvec'])# chi square from algorithm
    o=p[2]
    D=p[1]/2
    v=p[0]
    do=math.sqrt(pcov[2][2])*math.sqrt(s2/(len(fit)-3))
    dD=math.sqrt(pcov[1][1])*math.sqrt(s2/(len(fit)-3))/2.
    dv=math.sqrt(pcov[0][0])*math.sqrt(s2/(len(fit)-3))
    return (o,do,D,dD,v,dv)
            
def lq_diffusion_fit_constrained(times,msq_data,errors,p0):
    '''takes 3 arrays time and msq and  errors (SD or SEm) fits a diffusion model with 3 params\n
        y= (p[0]*x)**2+p[1]*x+p[2]
        return values are: parameters (a,b,c), fit at the x values and the covariance matrix.
        '''
    msq_data=np.array(msq_data)
    times=np.array(times)
    errors=np.array(errors)
    fitfunc = lambda p, x: (p[0]*x)**2+p[1]*x+p[2]# Target function
    def errfunc(p,times, msq_data,errors):
        if p[0]<0:
            return 10**10
        if p[1]<0:
            return 10**10
        if p[2]<0:
            return 10**10
        else:    
            return (msq_data-fitfunc(p, times))/errors
    p1,pcov,info,mesg,ier = optimize.leastsq(errfunc, p0, args=(times,msq_data,errors),full_output=True)#least square fit
    fit=fitfunc(p1,times)
    return p1,fit,pcov, info
    

