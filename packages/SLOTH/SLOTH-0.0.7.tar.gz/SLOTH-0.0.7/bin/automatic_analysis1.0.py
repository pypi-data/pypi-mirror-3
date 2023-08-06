#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 13:51:32 2012
 This file is part of SLOTH - stick/like object tracking in high-resolution.
    Copyright (C) 2012 Monika Kauer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
@author: monika
"""
import pylab
import Tkinter 
import tkFileDialog
from sloth import mean_square_analyser as msa
from sloth import data_reader
from sloth import image_processing as ip
from sloth import select_ROI_defs as sRd
import numpy as np
import csv
import os,sys, operator
import math


def weighted_mean(data, errs):
    """takes a list of data and errors and calculates weighted mean with error"""
    err=1./sum(map(lambda x: 1./x**2,errs))
    mean=err*sum(map(lambda x,y: x/y**2,data,errs))
    return mean,math.sqrt(err)
   
#==============================================================================
# Analysis of all ROIs reading from ROI file
#==============================================================================
def analyse_ROI(options, reader_options):
    name=options["RESULTS FILE"]
    max_displacement=options["PRECISION CUT OFF"] #in nm
    pixelsize=options["PIXEL SIZE"]
    framerate=options["FRAMERATE"]
    dt=options["TIME INTERVAL"]*framerate #in ms
    sampling=int(options["TIME INTERVAL"])
    inc=[]
    #==============================================================================
    # create and write to results file
    #==============================================================================
    if os.path.exists(name):
        fi = open(name,'a')
    else: 
        fi = open(name,'wa')
        fi.write("o,do,D,dD,v,dv, signalnoise, dsignalnoise, aslope, daslope, error, derror,N,v_lq,  dvlq, sampling, SNR\n")
    #==============================================================================
    # read ROI from files
    #==============================================================================
    roi=list()
    with open(options["ROI FILE"], 'r') as source:
        data=csv.reader(source,delimiter=' ')
        data.next()
        for k in data:
            roi.append([int(k[0]),int(k[1]),int(k[2]),int(k[3])])
    
    alldat=data_reader.Data_Reader(options["DATA FILE"])
    
    for region in roi:
        dat=alldat.get_object(region[0])
       
        
        if bool(region[1]-1):
            full_dat=data_reader.read_data(dat,[reader_options["2. LENGTH"], reader_options["2. ERROR"],reader_options["2. SLOPE"],reader_options["2. A"], reader_options["2. D"]])
        else:
            full_dat=data_reader.read_data(dat,[reader_options["1. LENGTH"], reader_options["1. ERROR"],reader_options["1. SLOPE"],reader_options["1. A"], reader_options["1. D"]])
          
        if options["SPEED FILTER"]:
            full_dat=np.transpose(data_reader.speed_filter(np.transpose(full_dat), options["MAXIMAL SPEED"], options["FRAMERATE"],options["PIXEL SIZE"]))        
            
        if options["PRECISION FILTER"]:
            full_dat=np.transpose(data_reader.error_filter(np.transpose(full_dat), options["PRECISION CUT OFF"], options["PIXEL SIZE"]))
        
        start=region[2]
        end=region[3]
        
        length=map(lambda x: x*options["PIXEL SIZE"],full_dat[0][start:end])
        err=map(lambda x: x*options["PIXEL SIZE"],full_dat[1][start:end])
        slope=full_dat[2][start:end]
        
        sn=map(lambda x,y: 1+x/y,full_dat[3][start:end],full_dat[4][start:end])#snr approx 1+a/d
        
       
        #==============================================================================
        # Analysis using Vesterberg method
        #==============================================================================
        v_lq,dvlq=sRd.growth_speed(length,framerate,True, start=0, end=None, output=False)
        
        
        if options["HISTOGRAM"]:
            for i in range(len(length)-1):
                inc.append(length[i+1]-length[i])
                continue
        if options["MSD LSQ FIT"]:
            o,do,D,dD,v,dv=msa.msq_from_data_lsq(length,framerate, v_lq/60.)
            SNR=(D*framerate/o)
        else:
            sampling=int(options["TIME INTERVAL"])
            for k in range(sampling, 50*int(options["TIME INTERVAL"])):
                o,do,D,dD,v,dv=msa.msq_from_data(length,framerate*k, k)
                SNR=(D*framerate*k/o)
                if SNR > 1.0 :
                    sampling=k
                    break
                else:
                    print SNR
                    continue  
            
        #==============================================================================
        # real units
        #=============================================================================
        o=o*10**-6
        do=do*10**-6
        v=v*60.
        dv=dv*60
        D=D*10**-3*60.
        dD=dD*10**-3*60.
        #==============================================================================
        # print on stdout
        #=============================================================================
        
        print ('D= %f4 +/- %f4 um^2/min'%(D, dD))
        print ('o= %f4 +/- %f4 um^2'%(o,do))
        print ('v= %f4 +/- %f4 um/min'%(v,dv))
        print ('SNR=%f4, K=%i'%(SNR,sampling) )
        print ('relative error:%f3')%(dD/D*100)
        if not options["MSD LSQ FIT"]:
            if SNR<1:
                print "SNR too small. Increase sampling!"
                continue
            
        #==============================================================================
        # Calculate average sn and slope etc  
        #==============================================================================
        signalnoise= np.average(sn)
        dsignalnoise=np.std(sn, ddof=1)/math.sqrt(len(sn))
        aslope=np.average(slope)
        daslope=np.std(slope, ddof=1)/math.sqrt(len(slope))
        error=np.average(err)
        derror=np.std(err, ddof=1)/math.sqrt(len(err))
        #==============================================================================
        # On and Off rates
        #==============================================================================
        fi.write('%f %f %f %f %f %f %f %f %f %f %f %f %i %f %f %i %f2\n'%(o,do,D,dD,v,dv, signalnoise, dsignalnoise, aslope, daslope, error, derror,len(length),v_lq, dvlq, sampling, SNR))
    if options["HISTOGRAM"]:
        pylab.hist(inc,20)  
        pylab.show()  
    print "->THE end. THE end."
    fi.close()
 

def main():
    options = {
         "WORKING DIRECTORY":"./",
         "PIXEL SIZE":105,
         "FRAMERATE":300,
         "SPEED FILTER": True, 
         "MAXIMAL SPEED":50,
         "PRECISION FILTER" : True,
         "PRECISION CUT OFF":100,
         "TIME INTERVAL":1,
         "ROI FILE": "./",
         "DATA FILE":"./",
         "RESULTS FILE":"results.dat",
         "MSD LSQ FIT": False,
         "HISTOGRAM":True
        }
        
    reader_options={
        "1. END x":2,
        "1. END y":3,
        "1. ERROR":11,
        "2. END x":4,
        "2. END y":5,
        "2. ERROR":12,
        "1. LENGTH":6,
        "2. LENGTH":7,
        "1. A":13,
        "2. A":14,
        "1. D":15,
        "2. D":16,
        "1. SLOPE":8,
        "2. SLOPE":9,
    }
    for arg in sys.argv[1:]:
        if "=" in arg:
            name, value = arg.split("=")
            name = name.replace("_", " ") 
        if type(options[name]) == float:
            value = float(value)
        elif type(options[name]) == int:
            value = int(value)
        elif type(options[name]) == bool:
            value = bool(int(value))
        options[name] = value

    
    master = Tkinter.Tk()
    master.title("Analyser")
    k = options.keys()   
    entries = {}
    row = 0
    for name in k:    
        Tkinter.Label(master,text=name.strip().capitalize()).grid(row=row,column=0,sticky=Tkinter.W,columnspan=2)
        if type(options[name]) == bool:
            entry = Tkinter.IntVar()
            c = Tkinter.Checkbutton(master, variable=entry)
            c.deselect()
            options[name] and c.select()
            c.grid(row=row,column=4)
        elif name=="WORKING DIRECTORY":
            fname1=Tkinter.StringVar()
            fname1.set(str(options[name]))
            def ask_dir(options=options,master=master, entry=entry):
                fname1.set(tkFileDialog.askdirectory(parent=master,initialdir=options["WORKING DIRECTORY"],title='Please select a working directory'))
                options[name]= fname1.get()
            entry = Tkinter.Button(master,textvariable=fname1, command=ask_dir)
            entry.grid(row=row,column=2,sticky=Tkinter.W,columnspan=3)
            
        elif name=="RESULTS FILE":
            fname2=Tkinter.StringVar()
            fname2.set(str(options[name]))
            def save_file(options=options,master=master, entry=entry):
                fname2.set(tkFileDialog.asksaveasfilename(parent=master,initialdir=fname1.get(),title='Please select a file for results'))
                options[name]= fname2.get()
            entry = Tkinter.Button(master,textvariable=fname2, command=save_file)
            entry.grid(row=row,column=2,sticky=Tkinter.W,columnspan=3)
                      
        elif type(options[name]) == str:
             entry = Tkinter.Button(master,text=str(options[name]))
             entry.grid(row=row,column=2,sticky=Tkinter.W,columnspan=5)
             def change_file(master=master, entry=entry):
                 fname = tkFileDialog.askopenfilename(parent=master,initialdir=fname1.get(),title='Please select a file')
                 entry["text"] = fname
             entry["command"]=change_file
        else:
            entry = Tkinter.Entry(master,bg='white',justify=Tkinter.LEFT,relief=Tkinter.SUNKEN,width=8)
            entry.delete(0,Tkinter.END)
            entry.insert(0,str(options[name]))
            entry.grid(row=row,column=4)
        entries[name] = entry
        row += 1
    
    ExitButton = Tkinter.Button(master,text='Exit',command=master.destroy)
    ExitButton.grid(row=row,column=0)
    def update_values():
        for name in entries:
                if isinstance(entries[name], Tkinter.Button):
                    v = (entries[name]["text"])
                    print v
                else:
                    v = entries[name].get()
                if type(options[name]) == float:
                    options[name] = float(v)
                elif type(options[name]) == int:
                    options[name] = int(v)
                else:             
                    options[name] = v
    def go_function():
        update_values()
        analyse_ROI(options, reader_options)
         
    GoButton = Tkinter.Button(master,text='Run', command=go_function)
    GoButton.grid(row=row,column=4)
    def average_results():
        '''prints averages of results to stdout'''
        update_values()
        win = Tkinter.Toplevel(master)
        win.title("Averaged results")
        data=list()
        values=[]
        f=open(options["RESULTS FILE"])
        f.next()
        dat=csv.reader(f,delimiter=' ', quoting=csv.QUOTE_NONNUMERIC)
        for k in dat:
            data.append([float(k[0]),float(k[1]),float(k[2]),float(k[3]),float(k[4]),float(k[5]),float(k[6]),float(k[7]),float(k[8]),float(k[9]),float(k[10]),float(k[11])])
        data=np.transpose(data)
        for i in range(0,len(data),2):
            values.append(weighted_mean(data[i],data[i+1]))
        print values
        text=Tkinter.Text(win,height=10,width=120)
        text.insert(1.0,'o,do,D,dD,v,dv, signalnoise, dsignalnoise, aslope, daslope, error, derror\n')
        text.insert(2.0,str(values))
        text.pack()
         
    ShowResults=Tkinter.Button(master,text='Show Averages', command=average_results)
    ShowResults.grid(row=row+1,column=2)
    def messageWindow():
    # create child window
        win = Tkinter.Toplevel(master)
        win.title("Select reader columns")
        key = reader_options.keys()
        key.sort()
        entries2 = {}
        row = 0
        for name in key:
            Tkinter.Label(win,text=name.strip().capitalize()).grid(row=row,column=0,sticky=Tkinter.W ,columnspan=2)
            entry = Tkinter.Spinbox(win,bg='white',justify=Tkinter.LEFT,relief=Tkinter.SUNKEN,width=4, from_=0,to=5*reader_options[name])
            entry.delete(0,Tkinter.END)
            entry.insert(0,str(reader_options[name]))
            entry.grid(row=row,column=4)
            row += 1
            entries2[name] = entry
        def update_options():
            for name in entries2:
                v = entries2[name].get()
                reader_options[name] = int(v)
        UpdateButton=Tkinter.Button(win, text='Update Options', command=update_options)
        UpdateButton.grid(row=row+1,column=0)
        OkButton=Tkinter.Button(win, text='OK', command=win.destroy)
        OkButton.grid(row=row+1,column=4)
    ReaderButton=Tkinter.Button(master, text='Change reader options', command=messageWindow)
    ReaderButton.grid(row=row,column=1)
    master.mainloop()

if __name__ == "__main__":
    main()
    
