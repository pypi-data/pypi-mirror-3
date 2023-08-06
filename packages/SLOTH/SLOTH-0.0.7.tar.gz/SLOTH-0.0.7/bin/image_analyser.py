#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 10:37:40 2011
@author: Monika Kauer
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
This routine automatically detects MTs in a tif movie, can find both Tkinter.ENDs and returns tip coordinates and plus and minus Tkinter.END length
1 For the first frame:
a) Some noise reduction, segmentation using watershed, for each region detect coordinates of maximal intensity
b) rotate a prototype of MT around maximum of intensity to find optimal direction
c) Fit Fermi-function to each Tkinter.END. The tip is defined as the coordinate where the intensity decreased to 0.5*Max(Intensity)
d) The found tip coordinates are saved as seed coordinates

2 For all following frames:
a) Probe the area around the tip of the seed within a certain angle (if extensions bend)
b) If there is a change in direction, fit a Fermifunction using the new direction, otherwise use old direction
c) tip1.x,tip1.y,tip2.x,tip2.y,l_plus,l_minus,slope1,slope2, brightness,err1.x, err1.y,err2.x, err2.y are written to separate files for each MT
d) length is defined as extension from tip coordinate (for static MTs it should therefore be roughly zero)

Error estimation:
The data used for the fit is found by a 1D linescan along the MT direction.The maximal error of the coordinate is the error in the one dimensional fit,
projected in the coordinate system of the picture. (Imagine the linescan is tilted by some angle with respect to the image coordinate system)
The error in the fit is estimate of the width of the decrase (like kT in the original Fermi function)

"""


#
#==============================================================================
# import modules
#==============================================================================
import os, sys
import numpy as np
import scipy
import Tkinter
import tkFileDialog
from sloth import image_processing as ip
from sloth import image_analyser_defs as iad
from sloth import vectorial,seed_detection
import matplotlib.pylab as py
from scipy import ndimage


def image_analyser(options):
    image_file=ip.MyImageFile(options[" FILE"], options["DUAL COLOR"], options["SHIFT"])
    #==============================================================================
    # Autodetect MTs
    #==============================================================================
    first_image = image_file.get_frame(0)
    if options["MEDIAN"]>2:
        first_image=ndimage.median_filter(first_image, options["MEDIAN"])
    objects = seed_detection.detect_objects(first_image, image_file.shape[0], image_file.shape[1], options["ALPHA"])
    x = seed_detection.fit_direction(first_image, objects)
    seed_coordinates=[]
    for coord in x:
        seed_coordinates.append(seed_detection.calculate_coordinates(coord[0], coord[1], options["LENGTH PROTOTYPE"]))
   
    #==============================================================================
    # Find preliminary directions by rotation around maximum in region
    # and increase length as far as possible, until no intensity is gained through elongation
    #==============================================================================
    seed_coordinates = seed_detection.FindOptimalDirections(first_image,seed_coordinates, image_file.shape[0],options)
    all_microtubules = iad.FineTuneCoordinates(first_image, seed_coordinates, options)

    all_microtubules = list(all_microtubules)
    print len(all_microtubules)
    if options["STOP"]:
        if options["GUI"]:
            fig1=py.figure(5)
            ip.ShowCoordinates(first_image, all_microtubules)
            py.ion()
            py.show()
            py.ioff()
        return 0

    #==============================================================================
    # Extracts Tip positions from all MTs in movie, writes to file
    #==============================================================================
    f = open('%s.dat'%(options[" FILE"]),'wa')
    f.write(str(options)+"\n")
    f.write("%s\n"%("#MT frame x1,y1,x2,y2, abs(l_plus),abs(l_minus), slope1,slope2, brightness, err1, err2, fit_a, fit_d, fit_a2,fit_d2"))
    drift = ip.tracker_data(options["DRIFT"])
    last_len=[]
    #last_len=[(10, 10)]*len(all_microtubules)
    for k in all_microtubules:
        last_len.append([abs(k[1])*0.5,abs(k[1])*0.5])
        
    data=list()
    for frame in range(0, image_file.number_frames):
        print "%i/%i"%(frame,image_file.number_frames-1)
        image = image_file.get_frame(frame)
        d=vectorial.Vector(0,0)
        if drift:
            d=vectorial.Vector(drift[frame][0]-drift[0][0],drift[frame][1]-drift[0][1])
        for k in range(len(all_microtubules)):
            l = iad.FindNewTip(image, all_microtubules[k], d, last_len[k], options)
            last_len[k] = l[0]
            if len(l) > 1:
#                data.append([frame,k,py.flatten(l[1:])])
                f.write("%d %d %s\n"%(k,frame," ".join(map(str, l[1:]))))
#    data=np.sort(np.array(data), axis=1)    
#    for line in data:
#        f.write("%s\n"%( " ".join(map(str,data))))
    f.close()           
#==============================================================================
# GUI FOR USER.
#==============================================================================

def main():
    options = {
     "ALPHA": 0.03,       # use lower value if too many small hits due to noise.
     "ELONGATION":0.85, #fraction of intensity at which object is elongated
     "STEP LENGTH" : 5, # number of pixels by which to elongate
     "LENGTH PROTOTYPE": 25, # average length of MT prototype
     "MINIMAL LENGTH": 5, # minimal length of seeds to detect (number of pixels)
     "END BENDING THRESHOLD": 0.8, # minimum intensity to change direction (if extensions are floppy)
     "MIN INTENSITY" : 0, # for 16bit image
     "BENDING ANGLE" : 5,# maximum angle at which the MT extensions are allowed to fluctuate
     "SCAN LENGTH FACTOR" : 1.2,#factor by which to elongate current length for scanning
     "TEST LENGTH" : 20, #number of pixels to scan for extension
     "MEDIAN" : 6,
     "DUAL COLOR": True,
     "STOP" : False,
     " FILE": "./",
     "DRIFT": "",
     "GUI" :  True,
     "SHIFT": 2.0
     }

    for arg in sys.argv[1:]:
        if "=" in arg:
            name, value = arg.split("=")
            name = name.replace("_", " ") 
        else:
            name, value = " FILE", arg
        if type(options[name]) == float:
            value = float(value)
        elif type(options[name]) == int:
            value = int(value)
        elif type(options[name]) == bool:
            value = bool(int(value))
        options[name] = value

    if not options["GUI"]:
        return image_analyser(options)

    master = Tkinter.Tk()
    master.title("Tracker")
    k = options.keys()
    k.remove("GUI")
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
                entry["text"] = x[0] + ": " + fname
            entry["command"]=change_file
        else:
            entry = Tkinter.Spinbox(master,bg='white',justify=Tkinter.LEFT,relief=Tkinter.SUNKEN,width=4, from_=0,to=5*options[name], increment=options[name]/10.)
            entry.delete(0,Tkinter.END)
            entry.insert(0,str(options[name]))
            entry.grid(row=row,column=4)
        entries[name] = entry
        row += 1

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
        image_analyser(options)
     

     
    GoButton = Tkinter.Button(master,text='Run', command=go_function)
    GoButton.grid(row=row,column=4)
    
    master.mainloop()


if __name__ == "__main__":
    main()
    
    
