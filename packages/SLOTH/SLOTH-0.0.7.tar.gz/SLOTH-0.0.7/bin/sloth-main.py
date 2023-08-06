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
"""
import Tkinter
import os
import tkFileDialog


def main():
    options = {
         "Tracking":"image_analyser.py",
         "ROI selection":"select_ROI.py",
         "MSD Analysis":"automatic_analysis1.0.py",
        }
        
    description="""SLOTH (stick-like object tracking in high resolution)\n 
    Copyright (C) 2012 Monika Kauer\n 
    GNU General Public License\n
    <http://www.gnu.org/licenses/>"""
    def about():
        win = Tkinter.Toplevel(master)
        win.title("About SLOTH")
        Tkinter.Label(win, text=description).pack()
        
    def set_workingDir():
        WDir=Tkinter.StringVar()
        WDir.set(tkFileDialog.askdirectory(parent=master,title='Please select a working directory'))
    
    #create master window   
    master = Tkinter.Tk()
    master.title("SLOTH")
    logo = Tkinter.PhotoImage(file="Sloth3.gif")
    Tkinter.Label(master,image=logo).grid(row=0,column=2,sticky=Tkinter.E,rowspan=4)
    #add menue bar
    menubar = Tkinter.Menu(master)
    
    menubar.add_command(label="About", command=about)
    menubar.add_command(label="Working Directory", command=set_workingDir)
    menubar.add_command(label="Exit", command=master.quit)
    master.config(menu=menubar)
    
    Tkinter.Button(master,text=str("Tracking"), command=lambda: os.system(options["Tracking"]) ).grid(row=0,column=0,sticky=Tkinter.W)
    Tkinter.Button(master,text=str("ROI selection"), command=lambda: os.system(options["ROI selection"])).grid(row=1,column=0,sticky=Tkinter.W)
    Tkinter.Button(master,text=str("MSD Analysis"), command=lambda: os.system(options["MSD Analysis"])).grid(row=2,column=0,sticky=Tkinter.W)
    Tkinter.Button(master,text="Exit", command=master.destroy).grid(row=3,column=0,sticky=Tkinter.W)

    master.mainloop()

if __name__ == "__main__":
    main()
    
