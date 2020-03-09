from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from Tkinter import *
import Tkinter as tk
import ntpath

import tkFileDialog,tkCommonDialog,tkSimpleDialog,tkMessageBox,tkColorChooser,ttk
from pygeoprocessing import routing
from pygeoprocessing import geoprocessing
import multiprocessing
import threading
from tqdm import tqdm
import os
import shutil
from shutil import copyfile
import numpy as np
import itertools
import math
import time
import shapefile
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from os import listdir
from os.path import isfile, join

import text_editor



global files,outputfiles,filesName,outputfilesName,window_TopLevelg,frame1,frame2,frame3
window_TopLevel={}
root = Tk()
root.title("DHM-WM")
root.resizable(width=True, height=True)
root.geometry("1350x750")

# root.state("zoomed")
def browses(root):
    # root.iconify()
    import browse
    root.iconify()
    browse.start(root)

def destroyWindow(file):
    global window_TopLevel
    print("Asdakhsgdsfajksashgd")
    try:
        window_TopLevel[file].destroy()
    except Exception as err:
        print(err)


def displayShapefile(file):
    global window_TopLevel
    window_TopLevel[file] = Toplevel(root)
    print(file)
    # sf = shapefile.Reader(
    #     "C:/Users/priyanshu/PycharmProjects/Purdue_Project/File/DHM/LREW_example/data_input/Vectors/reference_points.shp")
    sf2 = shapefile.Reader(file)
    fig = Figure(figsize=(6,6))
    a = fig.add_subplot(111)
    for shape in sf2.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        a.plot(x,y)
    canvas = Canvas(window_TopLevel[file], bg='#FFFFFF', width=500, height=500, scrollregion=(0, 0, 2000, 2000))
    hbar = Scrollbar(canvas, orient=HORIZONTAL)
    hbar.pack(side=BOTTOM, fill=X)
    hbar.config(command=canvas.xview)
    vbar = Scrollbar(canvas, orient=VERTICAL)
    vbar.pack(side=RIGHT, fill=Y)
    vbar.config(command=canvas.yview)
    canvas.config(width=500, height=500)
    canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
    figcanvas = FigureCanvasTkAgg(fig, canvas)
    figcanvas.get_tk_widget().pack(side=LEFT,expand=True)
    figcanvas.draw()



    canvas.pack(side=LEFT, expand=False, fill=BOTH)




def checkButtonInput(i,files,active):
    if active.get()==1:
        if i==0:
            None
        if i==1:
            displayShapefile(files)
        if i==2:
            global window_TopLevel
            window_TopLevel[file] = Toplevel(root)
            text_editor.openEditor(window_TopLevel[file],files)
    else:
        if i==0:
            None
        if i==1:
            destroyWindow(files)
        if i==2:
            None
def CreateFrames(files,outfiles):

    global frame1,frame2,frame3


    # =======================================================================================================================
    frame1 = Frame(root, width=250, height=300, bg="white", highlightbackground="Black", highlightcolor="Black",
                   highlightthickness=1)
    label11 = Label(frame1, text="Input Files", width=36).pack()

    canvas = tk.Canvas(frame1, bg='white', scrollregion=(0, 0, 400, 40000))
    canvas.pack(fill='both', expand=True)

    vbar = tk.Scrollbar(canvas, orient='vertical')
    vbar.pack(side='right', fill='y')
    vbar.config(command=canvas.yview)
    canvas.config(yscrollcommand=vbar.set)
    frame1.pack(anchor="nw")
    frame1.pack_propagate(0),
    # we need a container widget to put into the canvas
    # global f
    frame11 = tk.Frame(canvas)
    frame11.config(bg="white")
    arr = {}
    # you need to create a window into the canvas for the widget to scroll
    canvas.create_window((100, 0), window=frame11, anchor="n")
    varCount = 0
    if files is not None:
        for i in range(3):
            for j, jj in enumerate(files[i]):
                if jj is not 0:
                    arr[varCount] = tk.IntVar()
                    arr[varCount].set(0)
                    # widget must be packed into the container, not the canvas
                    tk.Checkbutton(frame11, bg="white", text=str(jj), activebackground="red", variable=arr[varCount],
                               command= lambda i=i,file=filesName[i][j],active=arr[varCount]:checkButtonInput(i,file,active)).pack(anchor="w")
                    varCount=varCount+1
            label12= Label(frame11,text="=======================",bg="white").pack()
    # =======================================================================================================================

    frame3 = Frame(root, width=250, height=300, bg="white", highlightbackground="Black", highlightcolor="Black",
                   highlightthickness=1)
    label31 = Label(frame3, text="Operations ", width=36).pack()
    frame3.pack(side="right", anchor="n")
    frame3.pack_propagate(0)
    canvas3 = tk.Canvas(frame3, bg='white', scrollregion=(0, 0, 400, 40000))
    canvas3.pack(fill='both', expand=True)

    vbar3 = tk.Scrollbar(canvas3, orient='vertical')
    vbar3.pack(side='right', fill='y')
    vbar3.config(command=canvas3.yview)
    canvas3.config(yscrollcommand=vbar3.set)

    # we need a container widget to put into the canvas
    frame36 = tk.Frame(canvas3)
    frame36.config(bg="white")
    arr3 = {}
    # you need to create a window into the canvas for the widget to scroll
    canvas3.create_window((100, 0), window=frame36, anchor="n")
    for i in range(0, 1000):
        arr3[i] = tk.IntVar()
        # widget must be packed into the container, not the canvas
        tk.Checkbutton(frame36, bg="white", text="heis sadihas" + str(i), variable=arr3[i], command=hello).pack()

    # =======================================================================================================================

    frame2 = Frame(root, width=250, height=300, bg="white", highlightbackground="Black", highlightcolor="Black",
                   highlightthickness=1)
    label21 = Label(frame2, text="Output Files", width=36).pack()
    frame2.pack(anchor="w")
    frame2.pack_propagate(0)
    canvas2 = tk.Canvas(frame2, bg='white', scrollregion=(0, 0, 400, 40000))
    canvas2.pack(fill='both', expand=True)

    vbar2 = tk.Scrollbar(canvas2, orient='vertical')
    vbar2.pack(side='right', fill='y')
    vbar2.config(command=canvas2.yview)
    canvas2.config(yscrollcommand=vbar2.set)

    # we need a container widget to put into the canvas
    frame22 = tk.Frame(canvas2)
    frame22.config(bg="white")
    arr2 = {}
    # you need to create a window into the canvas for the widget to scroll
    canvas2.create_window((100, 0), window=frame22, anchor="n")
    if files is not None:
        for i in range(2):
            for j, jj in enumerate(outputfiles[i]):
                if jj is not 0:
                    arr[varCount] = tk.IntVar()

                    # widget must be packed into the container, not the canvas
                    tk.Checkbutton(frame22, bg="white", text=str(jj), variable=arr[varCount],
                                   command=hello).pack(anchor="w")
                    varCount = varCount + 1
            label12 = Label(frame22, text="=======================", bg="white").pack()


def open():
    global frame1,frame2,frame3,filename,files,outputfiles,filesName,outputfilesName
    filename = tkFileDialog.askdirectory()
    files = [[0 for x in range(1000)] for y in range(3)]
    outputfiles = [[0 for x in range(300)], [0 for x in range(50000)]]
    filesName = [[0 for x in range(1000)] for y in range(3)]
    outputfilesName = [[0 for x in range(300)], [0 for x in range(50000)]]
    try:
         if filename != "" :
            try :
                frame1.destroy()
                frame2.destroy()
                frame3.destroy()

            except Exception as err:
                print(err)
            getfiles(filename)
    except Exception as err:
            print(err)



def getfiles(foldername):
    import os.path
    i = 0
    j = 0
    k = 0
    ii= 0
    jj= 0
    for dirpath, dirnames, filenames in os.walk(foldername):
        for filename in [f for f in filenames if f.endswith(".tif")]:
            parentFolder = os.path.basename(os.path.dirname(os.path.realpath(os.path.join(dirpath, filename))))
            fullFileName=(os.path.realpath(os.path.join(dirpath, filename)))

            if parentFolder == "Results" or parentFolder == "resultsFile":
                if not filename in outputfiles[1]:
                    outputfiles[1][ii]=filename
                    outputfilesName[1][ii]=fullFileName
                    ii=ii+1
            else:
                if not filename in files[0]:
                    files[0][i]=filename
                    filesName[0][i]=fullFileName
                    i = i+1

    for dirpath, dirnames, filenames in os.walk(foldername):
        for filename in [f for f in filenames if f.endswith(".shp")]:
            parentFolder = os.path.basename(os.path.dirname(os.path.realpath(os.path.join(dirpath, filename))))
            fullFileName = (os.path.realpath(os.path.join(dirpath, filename)))
            if parentFolder != "Results" and parentFolder != "resultsFile":
                if not filename in files[1]:
                    files[1][j] = filename
                    filesName[1][j]=fullFileName
                    j=j+1
    for dirpath, dirnames, filenames in os.walk(foldername):
        for filename in [f for f in filenames if f.endswith(".txt")]:
            parentFolder = os.path.basename(os.path.dirname(os.path.realpath(os.path.join(dirpath, filename))))
            fullFileName = (os.path.realpath(os.path.join(dirpath, filename)))
            if parentFolder == "Results" or parentFolder == "resultsFile":
                if not filename in outputfiles[0]:
                    outputfiles[0][jj]=filename
                    outputfilesName[0][jj]=fullFileName
                    jj=jj+1
            else:
                if not filename in files[2]:
                    files[2][k] =filename
                    filesName[2][k]=fullFileName
                    k=k+1
    # for file in files:
    #     print(file)
    CreateFrames(files,outputfiles)
    #
    # # subdirec=[name for name in os.listdir(".") if os.path.isdir(name)]
    # # files[0] = [f for f in listdir(folderPath) if isfile(join(folderPath, f))]
    # # for folders in subdirec:
    # #     if str(folders)!="Results" or str(folders) != "resultsFile":
    # #
    # for file in subdirec:
    #     print(str(file))


def hello():
    print "hello!"

menubar = Menu(root)

# create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="New", command=lambda:browses(root),  accelerator="Ctrl + N")
filemenu.add_command(label="Open", command=open ,accelerator="Ctrl + O")
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)


# create more pulldown menus
editmenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Edit", menu=editmenu)
editmenu.add_command(label="Cut", command=hello)
editmenu.add_command(label="Copy", command=hello)
editmenu.add_command(label="Paste", command=hello)


menubar.add_command(label="Text Editor",command=lambda:text_editor.openEditor(Toplevel(root)))

helpmenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="About", command=hello)


canvas =Canvas(root,width=1000,height=600)





# frame2=Frame(canvas,width=204,height=304,bg="white",highlightbackground="Black", highlightcolor="Black", highlightthickness=1)
# canvas2=Canvas(frame2,bg="white",width=200,height=300,highlightbackground="Black", highlightcolor="Black", highlightthickness=1,)
#
# canvas2.grid(row=0,column=0)
# frame2.grid(row=1,column=0, padx=10, pady=10)
# canvas2.grid_propagate(0)
# text=Label(canvas,text="asdasd").grid()
# # display the menu
# canvas.grid(row=0,column=0)
# canvas.grid_propagate(0)
root.config(menu=menubar)
root.mainloop()