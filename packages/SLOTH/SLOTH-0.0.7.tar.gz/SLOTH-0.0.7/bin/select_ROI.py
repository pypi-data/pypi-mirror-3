#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 10:18:04 2012
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
import Tkinter
import tkFileDialog
import subprocess as sub
import tkMessageBox
from sloth import data_reader
import pylab as py
import os,sys
import glob
from sloth import select_ROI_defs as sRd
import numpy as np

class TracePicker:
    def __init__(self, trace):
        self.coord = []
        self.key = False
        self.trace=trace
        self.identity=self.trace.get_label()
            
    def connect(self):
        'connect to all the events we need'
        self.cidpress = self.trace.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)
            
    def on_press(self, event):
        'on button press we will see if the mouse is over us and store some data'
        if event.inaxes != self.trace.axes: return
        contains, attrd = self.trace.contains(event)
        #if len(self.coord)>1: return
        if not contains: return
        self.coord.append(event.xdata)

    def disconnect(self):
        'disconnect all the stored connection ids'
        self.trace.figure.canvas.mpl_disconnect(self.cidpress)
     
 
def select_ROI(options, reader_options):
    img=options["IMAGE FILE"]
    i_l1=reader_options["1. LENGTH"]
    i_l2=reader_options["2. LENGTH"]
    i_t1x=reader_options["1. END x"]
    i_t1y=reader_options["1. END y"]
    i_t2x=reader_options["2. END x"]
    i_t2y=reader_options["2. END y"]
    
    py.ion()#switch to interactive mode
    roifile=str(options["DATA FILE"].split(".")[0])+"ROI.dat"
    if os.path.isfile(roifile):
        fi = open(roifile,'a')
    else: 
        fi = open(roifile,'wa')
        fi.write(str(options)+"\n")
    alldat=data_reader.Data_Reader(options["DATA FILE"])
    if options["SPECIFIC OBJECT"] !=-1:
        mts=[options["SPECIFIC OBJECT"]]
        
    else:
        mts=range(alldat.max)
        
    f = py.figure(1,figsize=(6,4))     
    for number in mts:
        dat=alldat.get_object(number)
        length1, length2 = data_reader.read_data(dat,[i_l1, i_l2])
        err1, err2 = data_reader.read_data(dat,[reader_options["1. ERROR"],reader_options["2. ERROR"]])   
            
        if options["SPEED FILTER"]:
            length1,err1=np.transpose(data_reader.speed_filter(np.transpose([length1,err1]), options["MAXIMAL SPEED"], options["FRAME RATE"],options["PIXEL SIZE"]))
            length2,err2=np.transpose(data_reader.speed_filter(np.transpose([length2,err2]), options["MAXIMAL SPEED"], options["FRAME RATE"],options["PIXEL SIZE"]))
        if options["PRECISION FILTER"]:
            length1,err1=np.transpose(data_reader.error_filter(np.transpose([length1,err1]), options["PRECISION CUT OFF"], options["PIXEL SIZE"]))
            length2,err2=np.transpose(data_reader.error_filter(np.transpose([length2,err2]), options["PRECISION CUT OFF"],options["PIXEL SIZE"]))
        
        l1=map(lambda x: x*options["PIXEL SIZE"], length1)
        l2=map(lambda x: x*options["PIXEL SIZE"], length2) 
         
        a = f.add_subplot(211)
        a.clear()
        b=f.add_subplot(212)
        b.clear()
        a.set_title("MT %i"%(number))
        a.hold(True)
        lines1=a.plot(l1,'-', color='red', label="1",picker=5)
        lines2=b.plot(l2,'-', color='blue', label="2",picker=5)
        a.plot(l1,'+', color='red')
        b.plot(l2,'+', color='blue')
        f.canvas.draw()
        tip1x,tip1y,tip2x,tip2y,length1, length2 = data_reader.read_data(dat,[i_t1x,i_t1y,i_t2x,i_t2y,i_l1, i_l2])
        if options["SHOW KYMO"]==True and os.path.isfile(options["IMAGE FILE"]):
            fig=py.figure(figsize=(4,6))
            sRd.make_kymo([tip1x,tip1y,tip2x,tip2y,length1, length2],img, options["FRAME RATE"], options["DUAL COLOR"])
            py.draw()
        f.canvas.flush_events()
        
        tr1=[]
        tr2=[]
        for line in lines1:
            l=TracePicker(line)
            l.connect()
            tr1.append(l)
        for line in lines2:
            l=TracePicker(line)
            l.connect()
            tr2.append(l)
    
        done=False
        while not done:
            done=py.waitforbuttonpress(timeout=60)
            if done==None:
                break
        if len(tr1[0].coord)>1:
            print "length1: %i %i %i %i\n"%(number,int(tr1[0].identity),tr1[0].coord[0],tr1[0].coord[1])
            v,dv=sRd.growth_speed(l1,options["FRAME RATE"], linreg=True,start=int(min(tr1[0].coord)), end=int(max(tr1[0].coord)), output=True)
            fi.write('%i %i %i %i %f3 %f3\n'%(number,int(tr1[0].identity),min(tr1[0].coord),max(tr1[0].coord),v,dv))
            
        if len(tr2[0].coord)>1:
            print "length2: %i %i %i %i\n"%(number,int(tr2[0].identity),tr2[0].coord[0],tr2[0].coord[1])   
            v2,dv2=sRd.growth_speed(l2,options["FRAME RATE"],linreg=True, start= int(min(tr2[0].coord)), end= int(max(tr2[0].coord)), output=True)   
            fi.write('%i %i %i %i %f3 %f3\n'%(number,int(tr2[0].identity),min(tr2[0].coord),max(tr2[0].coord),v2,dv2))
            
        py.figure(1)
        for t in tr1:
            t.disconnect()
        for t in tr2:
            t.disconnect()
        
        if options["SHOW KYMO"]==True and os.path.isfile(options["IMAGE FILE"]):
            py.close(fig)
    fi.close()            
    py.close(f)  
    py.close()    
    #py.ioff()
    
    

def main():
    options = {
        "FRAME RATE": 300,      
        "PIXEL SIZE" : 105,  
        "SPECIFIC OBJECT" :-1, 
        "DATA FILE": "./", 
        "IMAGE FILE": "./", 
        "SPEED FILTER": True, 
        "MAXIMAL SPEED":50,
        "PRECISION FILTER" : True,
        "PRECISION CUT OFF":100,
        "SHOW KYMO":True,
        "DUAL COLOR":True
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
        else:
            name, value = "IMAGE FILE", arg
        if type(options[name]) == float:
            value = float(value)
        elif type(options[name]) == int:
            value = int(value)
        elif type(options[name]) == bool:
            value = bool(int(value))
        options[name] = value
        
    master = Tkinter.Tk()
    master.title("ROI selection")
    k = options.keys()
    k.sort()
    entries = {}
    row = 0
    for name in k:
        Tkinter.Label(master,text=name.strip().capitalize()).grid(row=row,column=0,sticky=Tkinter.W,columnspan=2)
        if type(options[name]) == bool:
            entry = Tkinter.IntVar()
            c = Tkinter.Checkbutton(master, text="", variable=entry)
            c.deselect()
            options[name] and c.select()
            c.grid(row=row,column=4)
        elif type(options[name]) == str:
            entry = Tkinter.Button(master,text=name.strip().capitalize()+": "+str(options[name]))
            entry.grid(row=row,column=0,sticky=Tkinter.W,columnspan=5)
            
            def change_file(master=master, entry=entry):
                x= entry["text"].split(":")
                fname = ":".join(x[1:])[1:]
                fname = tkFileDialog.askopenfilename(parent=master,initialdir=os.path.split(fname)[0],title='Please select a file')
                entry["text"] = x[0] + ": " + str(fname)
            entry["command"]=change_file
        elif type(options[name])==float or type(options[name])==int:
            if type(options[name])==int: 
                entry = Tkinter.Spinbox(master,bg='white',justify=Tkinter.LEFT,relief=Tkinter.SUNKEN,width=4, from_=-10*abs(options[name]),to=10*abs(options[name]))
            else:
                entry = Tkinter.Spinbox(master,bg='white',justify=Tkinter.LEFT,relief=Tkinter.SUNKEN,width=4, from_=0,to=10*options[name], increment=options[name]/10.)
            entry.delete(0,Tkinter.END)
            entry.insert(0,str(options[name]))
            entry.grid(row=row,column=4)
        
        else:    
            entry = Tkinter.Entry(master,bg='white',justify=Tkinter.LEFT,relief=Tkinter.SUNKEN,width=4)
            entry.delete(0,Tkinter.END)
            entry.insert(0,str(options[name]))
            entry.grid(row=row,column=4)
        entries[name] = entry
        row += 1
    def call_movie():
        if os.path.isfile(options["IMAGE FILE"]):
            sRd.show_movie(options["IMAGE FILE"])
        else:
            tkMessageBox.showinfo('Show movie failed', 'Select an image file first.')
    MovieButton = Tkinter.Button(master,text='Show Movie',command=call_movie)
    MovieButton.grid(row=row,column=1)
    ExitButton = Tkinter.Button(master,text='Exit',command=master.destroy)
    ExitButton.grid(row=row,column=0)

    def go_function():
        for name in entries:
            if isinstance(entries[name], Tkinter.Button):
                v = ":".join(entries[name]["text"].split(":")[1:])[1:]
            else:
                v = entries[name].get()
            if type(options[name]) == float:
                options[name] = float(v)
            elif type(options[name]) == int:
                options[name] = int(v)
            else:             
                options[name] = v
        select_ROI(options, reader_options)
         
    GoButton = Tkinter.Button(master,text='Run', command=go_function)
    GoButton.grid(row=row,column=3)
    row+=1
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
