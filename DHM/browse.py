
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from Tkinter import *
import Tkinter as tk

import tkFileDialog, tkCommonDialog, tkSimpleDialog, tkMessageBox, tkColorChooser, ttk
from pygeoprocessing import routing

import threading
from tqdm import tqdm
import os

from shutil import copyfile
import numpy as np
import itertools
import math
import time
import shapefile
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import warnings

start_time = time.time()


def progressBar(progress, label, value):
    label.config(text=str(value) + "% completed")
    progress['value'] = value
    if value == 100:
        progress.destroy()
        label.grid_forget()
    root1.update_idletasks()


def displayShapefile():
    window = Toplevel(root1)

    sf = shapefile.Reader(
        "C:/Users/priyanshu/PycharmProjects/Purdue_Project/File/DHM/LREW_example/data_input/Vectors/reference_points.shp")
    sf2 = shapefile.Reader(
        "C:/Users/priyanshu/PycharmProjects/Purdue_Project/File/DHM/LREW_example/data_input/Vectors/watershed.shp")
    fig = Figure(figsize=(6, 6))
    a = fig.add_subplot(111)
    for shape in sf2.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        a.plot(x, y)
    canvas = Canvas(window, bg='#FFFFFF', width=500, height=500, scrollregion=(0, 0, 2000, 2000))
    hbar = Scrollbar(canvas, orient=HORIZONTAL)
    hbar.pack(side=BOTTOM, fill=X)
    hbar.config(command=canvas.xview)
    vbar = Scrollbar(canvas, orient=VERTICAL)
    vbar.pack(side=RIGHT, fill=Y)
    vbar.config(command=canvas.yview)
    canvas.config(width=500, height=500)
    canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
    figcanvas = FigureCanvasTkAgg(fig, canvas)
    figcanvas.get_tk_widget().pack(side=LEFT, expand=True)
    figcanvas.draw()

    canvas.pack(side=LEFT, expand=False, fill=BOTH)


def copyShapeFiles(orignal_input, destinationFile):
    src = ogr.Open(orignal_input)
    layer = src.GetLayerByIndex(0)
    driver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(destinationFile):
        driver.DeleteDataSource(destinationFile)
    ds = driver.CreateDataSource(destinationFile)
    destinationFile = destinationFile.encode('utf-8')
    dest_layer = ds.CreateLayer(destinationFile, srs=layer.GetSpatialRef(),
                                geom_type=layer.GetLayerDefn().GetGeomType())
    # feature = layer.GetFeature(1)
    outfeatureLayer = dest_layer.GetLayerDefn()
    layerDef = layer.GetLayerDefn()
    for i in range(layerDef.GetFieldCount()):
        dest_layer.CreateField(layerDef.GetFieldDefn(i))
    for feature in layer:
        outfeature = ogr.Feature(outfeatureLayer)
        for i in range(0, outfeatureLayer.GetFieldCount()):
            outfeature.SetField(outfeatureLayer.GetFieldDefn(i).GetNameRef(),
                                feature.GetField(i))

        ingeom = feature.GetGeometryRef()

        outfeature.SetGeometry(ingeom)
        dest_layer.CreateFeature(outfeature)
        outfeature.Destroy()


def getFileName(title, filetypes, rowno):
    if filetypes == "Text" or filetypes == "text":
        fileType = "Text"
        fileExtension = "*.txt"
    elif filetypes == "Shape" or filetypes == "shape":
        fileType = "Shape"
        fileExtension = "*.shp"
    elif filetypes == "Tiff" or filetypes == "tif":
        fileType = "Tiff"
        fileExtension = "*.tif"
    root1.filename = tkFileDialog.askopenfilename(initialdir="/", title=title,
                                                  filetypes=((fileType, fileExtension), ("All Files", "*.*")))
    head, tail = os.path.split(root1.filename)
    global inputVariables
    # inputVariables1 = [dem_uri,str_uri,outlet_uri,boundary_uri,watershed_uri]
    try:
        if type(root1.filename) is not None:
            if filetypes == "Text" or filetypes == "text":
                copyfile(root1.filename, textFolder + "/" + title + ".txt")
            elif filetypes == "Shape" or filetypes == "shape":
                copyShapeFiles(root1.filename, inputVectorFolder + "/" + title + ".shp")
            elif filetypes == "Tiff" or filetypes == "tif":
                copyfile(root1.filename, inputRasterFolder + "/" + title + ".tif")
            label3 = Label(frame, text=tail, bg="White").grid(row=rowno, column=1, sticky="W")

            if title == "DEM":
                global dem_uri
                dem_uri = inputRasterFolder + "/" + title + ".tif"
                print(dem_uri)
            elif title == "Streams":
                global str_uri
                str_uri = inputVectorFolder + "/" + title + ".shp"
            elif title == "Outlet":
                global outlet_uri
                outlet_uri = inputVectorFolder + "/" + title + ".shp"
            elif title == "Boundary":
                global boundary_uri
                global boundaryData
                boundaryData = True
                boundary_uri = inputVectorFolder + "/" + title + ".shp"
            elif title == "Watershed":
                global watershed_uri, original_watershed
                watershed_uri = inputVectorFolder + "/" + title + ".shp"
                original_watershed = inputVectorFolder + "/original_" + title + ".shp"
                copyShapeFiles(watershed_uri, original_watershed)
                print(watershed_uri)
            return root1.filename
    except Exception as err:
        return None


def getFileName2(title, filetypes, rowno, framen):
    if filetypes == "Text" or filetypes == "text":
        fileType = "Text"
        fileExtension = "*.txt"
    elif filetypes == "Shape" or filetypes == "shape":
        fileType = "Shape"
        fileExtension = "*.shp"
    elif filetypes == "Tiff" or filetypes == "tif":
        fileType = "Tiff"
        fileExtension = "*.tif"
    root1.filename = tkFileDialog.askopenfilename(initialdir="/", title=title,
                                                  filetypes=((fileType, fileExtension), ("All Files", "*.*")))
    head, tail = os.path.split(root1.filename)

    try:
        if type(root1.filename) is not None:
            if filetypes == "Text" or filetypes == "text":
                copyfile(root1.filename, textFolder + "/" + title + ".txt")
            elif filetypes == "Shape" or filetypes == "shape":
                copyShapeFiles(root1.filename, inputVectorFolder + "/" + title + ".shp")
            elif filetypes == "Tiff" or filetypes == "tif":
                copyfile(root1.filename, inputRasterFolder + "/" + title + ".tif")
            print(tail)

            if framen == "Untiled":
                label3 = Label(frame21, text=tail, bg="White").grid(row=rowno, column=1, sticky="W")
            elif framen == "Tiled":
                label3 = Label(frame22, text=tail, bg="White").grid(row=rowno, column=1, sticky="W")
            elif framen == "PET":
                label3 = Label(window, text=tail, bg="White").grid(row=rowno, column=1, sticky="W")

            if title == "Soil Raster":
                global soil_uri
                soil_uri = inputRasterFolder + "/" + title + ".tif"
                print(soil_uri)
            elif title == "Landuse Raster":
                global landuse_uri
                landuse_uri = inputRasterFolder + "/" + title + ".tif"
                print(landuse_uri)
            elif title == "Discharge Site":
                global sitesDischarge_uri
                sitesDischarge_uri = inputVectorFolder + "/" + title + ".shp"
            elif title == "reference points":
                global ref_point_uri
                ref_point_uri = inputVectorFolder + "/" + title + ".shp"
            elif title == "moisture sites":
                global sitesMoisture_uri
                sitesMoisture_uri = inputVectorFolder + "/" + title + ".shp"
            elif title == "Soil":
                global soilFile
                soilFile = textFolder + "/" + title + ".txt"
            elif title == "Landuse":
                global landuseFile
                landuseFile = textFolder + "/" + title + ".txt"
            elif title == "Precipitaion":
                global prcp_File
                prcp_File = textFolder + "/" + title + ".txt"
            elif title == "12 hour rain":
                global rainDis12_File
                rainDis12_File = textFolder + "/" + title + ".txt"
            elif title == "24 hour rain":
                global rainDis24_File
                rainDis24_File = textFolder + "/" + title + ".txt"
            elif title == "Temperature":
                global tmp_File
                tmp_File = textFolder + "/" + title + ".txt"
            elif title == "Abstraction":
                global cIa_d_File
                cIa_d_File = textFolder + "/" + title + ".txt"
            elif title == "root Depth":
                global RD_d_File
                RD_d_File = textFolder + "/" + title + ".txt"
            elif title == "hyd. Conductivity":
                haveDailyKc = True
                global Kc_d_File
                Kc_d_File = textFolder + "/" + title + ".txt"
            elif title == "Wind":
                global wind_File
                wind_File = textFolder + "/" + title + ".txt"
            elif title == "Sunshine":
                global SSD_File
                SSD_File = textFolder + "/" + title + ".txt"
            elif title == "Humidity":
                global humidity_File
                humidity_File = textFolder + "/" + title + ".txt"
            elif title == "PET":
                global PET_File
                PET_File = textFolder + "/" + title + ".txt"
            return root1.filename
    except Exception as err:
        return None

    try:
        if type(root1.filename) is not None:
            if title == "DEM":
                global dem_uri
                label31 = Label(frame, text=tail, bg="White").grid(row=3, column=1, sticky="W")
                copyfile(root1.filename, inputRasterFolder + "/dem.tif")
                dem_uri = inputRasterFolder + "/dem.tif"
                print(dem_uri)

            return root1.filename
    except Exception as err:
        return None


def makeFolders():
    if folderPath is not None:
        global outputGdb
        outputGdb = folderPath + '/Results'
        if not os.path.exists(outputGdb):
            os.makedirs(outputGdb)
        # Set the path of the folder that will be used to store the output text files
        global outputTxt
        outputTxt = folderPath + '/resultsFile'
        if not os.path.exists(outputTxt):
            os.makedirs(outputTxt)
        # Set the path of a folder that will be used to store temporary files
        global tempFolder
        tempFolder = folderPath + '/temp'
        if not os.path.exists(tempFolder):
            os.makedirs(tempFolder)
        global inputRasterFolder
        inputRasterFolder = folderPath + '/rasters'
        if not os.path.exists(inputRasterFolder):
            os.makedirs(inputRasterFolder)
        global inputVectorFolder
        inputVectorFolder = folderPath + '/vectors'
        if not os.path.exists(inputVectorFolder):
            os.makedirs(inputVectorFolder)
        global textFolder
        textFolder = folderPath + '/text'
        if not os.path.exists(textFolder):
            os.makedirs(textFolder)


def setDestination():
    global frame
    frame.grid_forget()
    frame = Frame(canvas, borderwidth=5, width=450, height=800, bg="White", highlightbackground="gray",
                  highlightcolor="gray", highlightthickness=3, )
    frame.grid(row=0, column=0)
    frame.grid_propagate(0)
    buttonFolder = Button(frame, text="Set Destination Folder", command=setDestination, width=20).grid(row=0, column=0,
                                                                                                       sticky="W")
    buttonr = Button(frame, text="display", command=displayShapefile, width=20).grid(row=0, column=1, sticky="W")
    filename = tkFileDialog.askdirectory()
    global folderPath
    global labelFolder
    labelFolder = Label(frame, text=filename, wraplength=250, bg="White").grid(row=0, column=1)
    folderPath = filename
    if folderPath != "":

        makeFolders()
        global rowno
        global filenames
        files = [['DEM'], ['Streams', 'Outlet', 'Boundary', 'Watershed']]
        filetype = [['DEM'], ['Streams', 'Outlet', 'Boundary', 'Watershed']]
        button = [['DEM'], ['Streams', 'Outlet', 'Boundary', 'Watershed']]
        rown = [[0], [1, 2, 3, 4]]
        for i, ii in enumerate(files):
            for j, jj in enumerate(files[i]):
                if i == 0:
                    filetype[i][j] = "Tiff"
                elif i == 1:
                    filetype[i][j] = "Shape"
                elif i == 2:
                    filetype[i][j] = "text"
                if j == 0:
                    label = Label(frame, text="Enter " + filenames[i] + " files", width=20, bg="White").grid(row=rowno,
                                                                                                             column=0)
                    rowno = rowno + 1
                rown[i][j] = rowno
                rowno = rowno + 1
                button[i][j] = Button(frame, text="Import " + files[i][j] + " file",
                                      command=lambda i=i, j=j: getFileName(files[i][j], filetype[i][j], rown[i][j]),
                                      width=20, bg="green").grid(row=rown[i][j], column=0, sticky="W")

        buttonProcess = Button(frame, text="Start Processing", command=startProcess, width=20, bg="orange").grid(
            row=rowno, column=1, sticky="W")
        rowno = rowno + 1
        # print(folderPath)



def startDHM(model):
    global frame21, frame22, rowno, fdr_uri, stream_uri, haveDisPrcp, haveDailyKc, haveDailyPET, DisPrcpFolder, Kc_d_File, PET_File
    startDay = startDate.get()
    endDay = endDate.get()
    dayRouting = routingDay.get()
    fdr_uri = inputRasterFolder + '/fdr.tif'
    stream_uri = inputVectorFolder + '/stream_DL.shp'
    if haveDisPrcp == False:
        DisPrcpFolder = "Empty"
        print("Empty3")
    if haveDailyKc == False:
        print("Empty1")
        Kc_d_File = "Empty"
    if haveDailyPET == False:
        PET_File = "Empty"
        print("Empty2")
    if model == "Untiled":
        outlet_name = "I"
        if PET_method == 2:
            Untiled_DHM_Function(frame21, rowno, inputRasterFolder, inputVectorFolder, outputGdb, outputTxt, tempFolder,
                                 outlet_name,
                                 fdr_uri, soil_uri, landuse_uri, dem_uri, original_watershed, stream_uri,
                                 sitesDischarge_uri,
                                 sitesMoisture_uri, ref_point_uri, landuseFile, soilFile, prcp_File, rainDis12_File,
                                 rainDis24_File, tmp_File, RD_d_File, haveDailyPET, PET_method, haveDailyKc, Kc_d_File,
                                 cIa_d_File, startDay, endDay, dayRouting, haveDisPrcp, DisPrcpFolder, PET_File,
                                 wind_File,
                                 SSD_File, humidity_File)

        elif PET_method == 1:
            Untiled_DHM_Function(frame21, rowno, inputRasterFolder, inputVectorFolder, outputGdb, outputTxt, tempFolder,
                                 outlet_name,
                                 fdr_uri, soil_uri, landuse_uri, dem_uri, original_watershed, stream_uri,
                                 sitesDischarge_uri,
                                 sitesMoisture_uri, ref_point_uri, landuseFile, soilFile, prcp_File, rainDis12_File,
                                 rainDis24_File, tmp_File, RD_d_File, haveDailyPET, PET_method, haveDailyKc, Kc_d_File,
                                 cIa_d_File, startDay, endDay, dayRouting, PET_File, haveDisPrcp, DisPrcpFolder, )
        elif PET_method == 0:
            Untiled_DHM_Function(frame21, rowno, inputRasterFolder, inputVectorFolder, outputGdb, outputTxt, tempFolder,
                                 outlet_name,
                                 fdr_uri, soil_uri, landuse_uri, dem_uri, original_watershed, stream_uri,
                                 sitesDischarge_uri,
                                 sitesMoisture_uri, ref_point_uri, landuseFile, soilFile, prcp_File,
                                 rainDis12_File,
                                 rainDis24_File, tmp_File, RD_d_File, haveDailyPET, PET_method, haveDailyKc,
                                 Kc_d_File, cIa_d_File, startDay, endDay, dayRouting, haveDisPrcp, DisPrcpFolder,
                                 PET_File)
    if model == "Tiled":
        outlet_name = "AXL"
        if PET_method == 2:
            Tiled_DHM_Function(frame22, rowno, inputRasterFolder, inputVectorFolder, outputGdb, outputTxt, tempFolder,
                               outlet_name,
                               fdr_uri, soil_uri, landuse_uri, dem_uri, original_watershed, stream_uri,
                               sitesDischarge_uri, landuseFile, soilFile, prcp_File,
                               rainDis12_File, rainDis24_File, tmp_File, haveDailyPET, PET_method, haveDailyKc,
                               Kc_d_File, cIa_d_File, startDay, endDay, dayRouting, haveDisPrcp,
                               DisPrcpFolder, PET_File, wind_File, SSD_File, humidity_File)
        elif PET_method == 1:
            Tiled_DHM_Function(frame22, rowno, inputRasterFolder, inputVectorFolder, outputGdb, outputTxt, tempFolder,
                               outlet_name,
                               fdr_uri, soil_uri, landuse_uri, dem_uri, original_watershed, stream_uri,
                               sitesDischarge_uri, landuseFile, soilFile, prcp_File,
                               rainDis12_File, rainDis24_File, tmp_File, haveDailyPET, PET_method,
                               haveDailyKc,
                               Kc_d_File, cIa_d_File, startDay, endDay, dayRouting)
        elif PET_method == 0:
            Tiled_DHM_Function(frame22, rowno, inputRasterFolder, inputVectorFolder, outputGdb, outputTxt, tempFolder,
                               outlet_name,
                               fdr_uri, soil_uri, landuse_uri, dem_uri, original_watershed, stream_uri,
                               sitesDischarge_uri, landuseFile, soilFile, prcp_File,
                               rainDis12_File, rainDis24_File, tmp_File, haveDailyPET, PET_method,
                               haveDailyKc,
                               Kc_d_File, cIa_d_File, startDay, endDay, dayRouting, PET_File)


def startProcess2():
    def windowDestroy():
        global window
        try:
            window.destroy()
        except Exception as err:
            print(err)

    def setPET(method, rowno=None):
        global buttonFAO
        global filenames
        global value
        global PET_method

        filesFAO = ['Wind', 'Sunshine', 'Humidity']
        if method == "FAO":
            PET_method = 2
            global window
            window = tk.Toplevel(root1)
            window.geometry("300x300")
            rownFAO = [1, 2, 3]
            buttonFAO = ['Wind', 'Sunshine', 'Humidity']
            value = True
            for i, ii in enumerate(filesFAO):
                rownFAO[i] = rowno
                rowno = rowno + 1
                buttonFAO[i] = Button(window, text="Import " + filesFAO[i] + " file",
                                      command=lambda i=i: getFileName2(filesFAO[i], "text", rownFAO[i], "PET"),
                                      width=20, bg="green").grid(row=rowno, column=0, sticky="W")
            buttonDestroy = Button(window, text="Ok", command=windowDestroy, width=20, bg="orange").grid(row=4,
                                                                                                         column=0)
        elif method == "Hargreaves":
            PET_method = 1
            if value:
                global wind_File, SSD_File, humidity_File
                wind_File = None
                SSD_File = None
                humidity_File = None
            print("asdasd")
            windowDestroy()
        elif method == "file":
            global haveDailyPET
            haveDailyPET = True
            getFileName2("PET", "Text", rowno, "Untiled")
            PET_method = 0
            windowDestroy()

        if method == "Kc_d":
            global haveDailyKc
            haveDailyKc = True
            getFileName2("hyd. Conductivity", "Text", rowno, "Untiled")

    def DisPrcp():
        global DisPrcpFolder, haveDisPrcp
        DisPrcpFolder = tkFileDialog.askdirectory()
        haveDisPrcp = True

    def UntiledModule():
        global frame22
        frame22.grid_forget()
        frame22 = Frame(canvas, borderwidth=5, width=300, height=800, bg="White", highlightbackground="gray",
                        highlightcolor="gray", highlightthickness=3, )
        frame22.grid(row=0, column=2)
        frame22.grid_propagate(0)
        buttonR32 = Radiobutton(frame22, text="Tiled", variable="untiled", command=TiledModule, width=20,
                                value=1).grid(row=0, column=0, sticky="w")
        global rowno
        global filenames
        rowno = 3
        files = [['Soil Raster', 'Landuse Raster'],
                 ['Discharge Site', 'reference points', 'moisture sites'],
                 ['Soil', 'Landuse', 'Precipitaion', '12 hour rain', '24 hour rain', 'Temperature', 'Abstraction',
                  'root Depth']]
        filetype = [['Soil Raster', 'Landuse Raster'],
                    ['Discharge Site', 'reference points', 'moisture sites'],
                    ['Soil', 'Landuse', 'Precipitaion', '12 hour rain', '24 hour rain', 'Temperature', 'Abstraction',
                     'root Depth']]
        button = [['Soil Raster', 'Landuse Raster'],
                  ['Discharge Site', 'reference points', 'moisture sites'],
                  ['Soil', 'Landuse', 'Precipitaion', '12 hour rain', '24 hour rain', 'Temperature', 'Abstraction',
                   'root Depth']]
        rown = [[1, 2], [1, 2, 3], range(1, 20)]
        for i, ii in enumerate(files):
            for j, jj in enumerate(files[i]):
                if i == 0:
                    filetype[i][j] = "Tiff"
                elif i == 1:
                    filetype[i][j] = "Shape"
                elif i == 2:
                    filetype[i][j] = "text"
                if j == 0:
                    label = Label(frame21, text="Enter " + filenames[i] + " files", width=20, bg="White").grid(
                        row=rowno, column=0, sticky='w')
                    rowno = rowno + 1
                rown[i][j] = rowno
                rowno = rowno + 1
                button[i][j] = Button(frame21, text="Import " + files[i][j] + " file",
                                      command=lambda i=i, j=j: getFileName2(files[i][j], filetype[i][j], rown[i][j],
                                                                            "Untiled"), width=22, bg="green").grid(
                    row=rown[i][j], column=0, sticky="W")
        buttonPET1 = Radiobutton(frame21, text="PET File", variable="PET", command=lambda i=rowno: setPET("file", i),
                                 width=20,
                                 value=2, bg="Orange").grid(row=rowno, column=0, sticky="w")
        rowno = rowno + 1
        buttonPET1 = Radiobutton(frame21, text="Hargreaves", variable="PET", command=lambda: setPET("Hargreaves"),
                                 width=20,
                                 value=0, bg="Orange").grid(row=rowno, column=0, sticky="w")
        rowno = rowno + 1
        buttonPET1 = Radiobutton(frame21, text="FAO Penman-Monteith", variable="PET", command=lambda: setPET("FAO"),
                                 width=20,
                                 value=1, bg="Orange").grid(row=rowno, column=0, sticky="w")
        rowno = rowno + 1
        rowno = rowno + 1
        buttonPET1 = Radiobutton(frame21, text="Hyd. Conductivity file", variable="KC",
                                 command=lambda i=rowno: setPET("Kc_d", i),
                                 width=20,
                                 value=1, bg="Green").grid(row=rowno, column=0, sticky="w")
        rowno = rowno + 1
        global startDate, endDate, routingDay
        label = Label(frame21, text="Start Date", bg="White").grid(row=rowno, column=0)
        startDate = Entry(frame21)
        startDate.insert(END, 'yyyy-mm-dd')
        startDate.grid(row=rowno, column=1)
        rowno = rowno + 1
        label = Label(frame21, text="Routing Date", bg="White").grid(row=rowno, column=0)
        routingDay = Entry(frame21)
        routingDay.insert(END, 'yyyy-mm-dd')
        routingDay.grid(row=rowno, column=1)
        rowno = rowno + 1
        label = Label(frame21, text="End Date", bg="White").grid(row=rowno, column=0)
        endDate = Entry(frame21)
        endDate.insert(END, "yyyy-mm-dd")
        endDate.grid(row=rowno, column=1)
        rowno = rowno + 1
        buttonDisPrcp = Button(frame21, text="Distributed Precipitation Folder", command=DisPrcp, width=20,
                               bg="green").grid(row=rowno, column=0)
        rowno = rowno + 1
        buttonDHM = Button(frame21, text="RUN MODEL", command=lambda: startDHM("Untiled"), width=20, bg="Orange").grid(
            row=rowno, column=1)

    def TiledModule():
        global frame21
        frame21.grid_forget()
        frame21 = Frame(canvas, borderwidth=5, width=300, height=800, bg="White", highlightbackground="gray",
                        highlightcolor="gray", highlightthickness=3, )
        frame21.grid(row=0, column=1)
        frame21.grid_propagate(0)
        buttonR31 = Radiobutton(frame21, text="Untiled", variable="Untiled", command=UntiledModule, width=20,
                                value=0).grid(
            row=0, column=0, sticky="w")

        global rowno
        global filenames
        rowno = 3
        files = [['Soil Raster', 'Landuse Raster'],
                 ['Discharge Site'],
                 ['Soil', 'Landuse', 'Precipitaion', '12 hour rain', '24 hour rain', 'Temperature', 'Abstraction']]
        filetype = [['Soil Raster', 'Landuse Raster'],
                    ['Discharge Site'],
                    ['Soil', 'Landuse', 'Precipitaion', '12 hour rain', '24 hour rain', 'Temperature', 'Abstraction']]
        button = [['Soil Raster', 'Landuse Raster'],
                  ['Discharge Site'],
                  ['Soil', 'Landuse', 'Precipitaion', '12 hour rain', '24 hour rain', 'Temperature', 'Abstraction']]
        rown = [[1, 2], [1, 2, 3], range(1, 20)]
        for i, ii in enumerate(files):
            for j, jj in enumerate(files[i]):
                if i == 0:
                    filetype[i][j] = "Tiff"
                elif i == 1:
                    filetype[i][j] = "Shape"
                elif i == 2:
                    filetype[i][j] = "text"
                if j == 0:
                    label = Label(frame22, text="Enter " + filenames[i] + " files", width=20, bg="White").grid(
                        row=rowno,
                        column=0,
                        sticky='w')
                    rowno = rowno + 1
                rown[i][j] = rowno
                rowno = rowno + 1
                button[i][j] = Button(frame22, text="Import " + files[i][j] + " file",
                                      command=lambda i=i, j=j: getFileName2(files[i][j], filetype[i][j], rown[i][j],
                                                                            "Tiled"), width=20, bg="green").grid(
                    row=rown[i][j], column=0, sticky="W")
        buttonPET1 = Radiobutton(frame22, text="PET File", variable="PET", command=lambda i=rowno: setPET("file", i),
                                 width=20,
                                 value=2, bg="Orange").grid(row=rowno, column=0, sticky="w")
        rowno = rowno + 1
        buttonPET1 = Radiobutton(frame22, text="Hargreaves", variable="PET", command=lambda: setPET("Hargreaves"),
                                 width=20,
                                 value=0, bg="orange").grid(row=rowno, column=0, sticky="w")
        rowno = rowno + 1
        buttonPET1 = Radiobutton(frame22, text="FAO Penman-Monteith", variable="PET", command=lambda: setPET("FAO"),
                                 width=20,
                                 value=1, bg="orange").grid(row=rowno, column=0, sticky="w")
        rowno = rowno + 1
        buttonPET1 = Radiobutton(frame22, text="Hyd. Conductivity file", variable="KC",
                                 command=lambda i=rowno: setPET("Kc_d", i),
                                 width=20,
                                 value=1, bg="Green").grid(row=rowno, column=0, sticky="w")
        rowno = rowno + 1
        global startDate, endDate, routingDay
        label = Label(frame22, text="Start Date", bg="White").grid(row=rowno, column=0)
        startDate = Entry(frame22)
        startDate.insert(END, 'yyyy-mm-dd')
        startDate.grid(row=rowno, column=1)
        rowno = rowno + 1
        label = Label(frame22, text="Routing Date", bg="White").grid(row=rowno, column=0)
        routingDay = Entry(frame22)
        routingDay.insert(END, 'yyyy-mm-dd')
        routingDay.grid(row=rowno, column=1)
        rowno = rowno + 1
        label = Label(frame22, text="End Date", bg="White").grid(row=rowno, column=0)
        endDate = Entry(frame22)
        endDate.insert(END, "yyyy-mm-dd")
        endDate.grid(row=rowno, column=1)
        rowno = rowno + 1
        global DisPrcpFolder
        buttonDisPrcp = Button(frame22, text="Distributed Precipitation Folder", command=DisPrcp, width=20,
                               bg="green").grid(row=rowno, column=0)
        rowno = rowno + 1
        buttonDHM = Button(frame22, text="RUN MODEL", command=lambda: startDHM("Tiled"), width=20, bg="Orange").grid(
            row=rowno, column=1)

    buttonR31 = Radiobutton(frame21, text="Untiled", variable="Untiled", command=UntiledModule, width=20, value=1).grid(
        row=0, column=0, sticky="w")
    buttonR32 = Radiobutton(frame22, text="Tiled", variable="Untiled", command=TiledModule, width=20,
                            value=2).grid(row=0, column=0, sticky="e")


def startProcess():
    if folderPath is not None:
        watershed_one = True
        if watershed_one:
            startProcess2()
        try:
            watershed_one = watershedPreparation(dem_uri, str_uri, outlet_uri, watershed_uri, boundary_uri)
            watershed_one = True
            if watershed_one:
                startProcess2()

        except Exception as err:
            tkMessageBox.showerror("Error", "All parameters not Satisfied\n" + str(err), icon='warning')
            print("All parameters not Satisfied")
            print(err)
    else:
        print("Set Destination Folder")



def watershedPreparation(dem_uri, str_uri, outlet_uri, watershed_uri, boundary_uri):
    start_time = time.time()
    str_crt = 120  # Set stream criteria: the number of upstream grid cells
    global rowno
    progress = ttk.Progressbar(frame, orient=HORIZONTAL, length=150, mode='determinate')
    progress.grid(row=rowno, column=1, sticky="W")
    label = Label(frame, bg="White")
    label.grid(row=rowno + 1, column=1, sticky="W")
    progressBar(progress, label, 10)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Input data and parameters are set above.
    Do not change content below, unless you would modify the script.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    # Prepare some paremeters
    dem_ds = gdal.Open(dem_uri)
    geotransform = dem_ds.GetGeoTransform()
    cellSize = (abs(geotransform[1]) + abs(geotransform[5])) / 2
    print(cellSize)
    del geotransform
    # Read dem data into a numpy array named dem_og
    dem_og = dem_ds.ReadAsArray()
    dem_ds = None

    """Watershed preparation analysis, create flow direction raster, stream raster"""

    # Create a raster with the same extent, projection with the dem raster, but with 0 values.
    def make_constant_raster_from_base(base_dataset_uri, constant_value, out_uri, out_datatype=None, nodata_value=None):
        base_ds = gdal.Open(base_dataset_uri)
        gt_gdal = base_ds.GetGeoTransform()
        prj_gdal = base_ds.GetProjectionRef()
        if out_datatype == None:
            out_datatype = base_ds.GetRasterBand(1).DataType
        out_ds = gdal.GetDriverByName("GTiff").Create(out_uri, base_ds.RasterXSize, base_ds.RasterYSize,
                                                      base_ds.RasterCount, eType=out_datatype)
        out_ds.SetGeoTransform(gt_gdal)
        out_ds.SetProjection(prj_gdal)
        base_arr = base_ds.ReadAsArray()
        ndv = base_ds.GetRasterBand(1).GetNoDataValue()
        if nodata_value == None:
            nodata_value = ndv
        out_arr = np.where(base_arr != ndv, constant_value, nodata_value)
        out_ds.GetRasterBand(1).WriteArray(out_arr)
        out_ds.GetRasterBand(1).SetNoDataValue(nodata_value)
        base_ds = None
        out_ds = None

    make_constant_raster_from_base(dem_uri, 0.0, tempFolder + "/zero_raster.tif")
    zero_ds = gdal.Open(tempFolder + "/zero_raster.tif", gdal.GA_ReadOnly)
    # Convert streamFeature to streamRaster
    str_ds = ogr.Open(str_uri)
    str_ly = str_ds.GetLayer(0)
    stream_ds = gdal.GetDriverByName("GTiff").CreateCopy(tempFolder + "/stream_og.tif", zero_ds, strict=0)
    gdal.RasterizeLayer(stream_ds, [1], str_ly, burn_values=[600])
    stream_og = stream_ds.ReadAsArray()
    # %%%%%%% new 1 line added %%%%%%%
    zero_ds = None
    str_ds = None
    progressBar(progress, label, 20)

    # Build a wall at the watershed boundary, if boundaryData is ture
    def createBuffer(inputfn, outputBufferfn, bufferDist):
        inputds = ogr.Open(inputfn)
        inputlyr = inputds.GetLayer(0)
        srs = inputlyr.GetSpatialRef()

        shpdriver = ogr.GetDriverByName('ESRI Shapefile')
        if os.path.exists(outputBufferfn):
            shpdriver.DeleteDataSource(outputBufferfn)
        outputBufferds = shpdriver.CreateDataSource(outputBufferfn)
        outputBufferfn = outputBufferfn.encode('utf-8')
        bufferlyr = outputBufferds.CreateLayer(outputBufferfn, srs=srs, geom_type=ogr.wkbPolygon)
        featureDefn = bufferlyr.GetLayerDefn()

        for feature in inputlyr:
            ingeom = feature.GetGeometryRef()
            geomBuffer = ingeom.Buffer(bufferDist)

            outFeature = ogr.Feature(featureDefn)
            outFeature.SetGeometry(geomBuffer)
            bufferlyr.CreateFeature(outFeature)
            outFeature.Destroy()

        inputds = None
        outputBufferds = None

    progressBar(progress, label, 30)
    if boundaryData == True:
        dem_ds = gdal.Open(dem_uri, gdal.GA_ReadOnly)
        createBuffer(boundary_uri, tempFolder + "/wall1.shp", 2 * cellSize)
        createBuffer(boundary_uri, tempFolder + "/wall2.shp", cellSize)
        wall1_ds = ogr.Open(tempFolder + "/wall1.shp")
        wall1_ly = wall1_ds.GetLayer(0)
        wall2_ds = ogr.Open(tempFolder + "/wall2.shp")
        wall2_ly = wall2_ds.GetLayer(0)
        dem_Wall_ds = gdal.GetDriverByName("GTiff").CreateCopy(tempFolder + "/dem_Wall.tif", dem_ds, strict=0)
        dem_ds = None
        gdal.RasterizeLayer(dem_Wall_ds, [1], wall1_ly, burn_values=[600], options=["MERGE_ALG=ADD"])
        gdal.RasterizeLayer(dem_Wall_ds, [1], wall2_ly, burn_values=[600], options=["MERGE_ALG=ADD"])
        dem_Wall = dem_Wall_ds.ReadAsArray()
        dem_Wall = np.where(stream_og == 600, dem_og, dem_Wall)
        dem_Wall_ds.GetRasterBand(1).WriteArray(dem_Wall)
        wall1_ds = None
        wall2_ds = None
        progressBar(progress, label, 40)
    # Burn DEM with streams
    if boundaryData == True:
        dem_Burn_ds = gdal.GetDriverByName("GTiff").CreateCopy(tempFolder + "/dem_burn.tif", dem_Wall_ds, strict=0)
        dem_Burn_arr = dem_Wall - stream_og
        dem_Wall_ds = None
    else:
        dem_ds = gdal.Open(dem_uri, gdal.GA_ReadOnly)
        dem_Burn_ds = gdal.GetDriverByName("GTiff").CreateCopy(tempFolder + "/dem_burn.tif", dem_ds, strict=0)
        dem_Burn_arr = dem_og - stream_og
        dem_ds = None
    dem_Burn_ds.GetRasterBand(1).WriteArray(dem_Burn_arr)
    dem_Burn_ds = None
    stream_ds = None
    # Fill DEM pits
    progressBar(progress, label, 60)
    routing.routing.fill_pits(tempFolder + "/dem_burn.tif", tempFolder + "/dem_fill.tif")
    # Do flow direction
    routing.routing.flow_direction_d_inf(tempFolder + "/dem_fill.tif", tempFolder + "/fdr.tif")
    # Do flow accumulation
    routing.routing.flow_accumulation(tempFolder + "/fdr.tif", tempFolder + "/dem_fill.tif", tempFolder + "/fac.tif")
    # Delineate study watershed
    routing.routing.delineate_watershed(tempFolder + "/dem_fill.tif", outlet_uri, 5 * cellSize, str_crt,
                                        watershed_uri, inputVectorFolder + "/outlet_modified.shp",
                                        tempFolder + "/stream_out.tif")
    watershed_uri = original_watershed

    # Designe a function to clip a GeoTiff raster with a Shapefile polygon (the polygon extent is equal to or smaller than the raster extent)
    def clip_GeoTiff_with_polygon(raster_input_uri, raster_output_uri, polygon_uri):
        """ Clip a GeoTiff raster within the mask of a polygon dataset """
        # Get the information of input raster and polygon
        raster_ds = gdal.Open(raster_input_uri, gdal.GA_ReadOnly)
        raster_arr = raster_ds.ReadAsArray()
        raster_geotransform = raster_ds.GetGeoTransform()
        ndv = raster_ds.GetRasterBand(1).GetNoDataValue()
        raster_datatype = raster_ds.GetRasterBand(1).DataType
        x_min_ras, y_max_ras = raster_geotransform[0], raster_geotransform[3]
        pixelSize = (abs(raster_geotransform[1]) + abs(raster_geotransform[5])) / 2
        vector_ds = ogr.Open(polygon_uri)
        vector_ly = vector_ds.GetLayer(0)
        source_srs = vector_ly.GetSpatialRef()
        x_min, x_max, y_min, y_max = vector_ly.GetExtent()
        x_res = int(round((x_max - x_min) / pixelSize))
        y_res = int(round((y_max - y_min) / pixelSize))
        # Create a output raster from the input polygon
        out_ras_ds = gdal.GetDriverByName("gtiff").Create(raster_output_uri, x_res, y_res, 1, raster_datatype)
        type(out_ras_ds)
        out_ras_ds.SetProjection(source_srs.ExportToWkt())
        out_ras_ds.SetGeoTransform([x_min, pixelSize, 0, y_max, 0, -pixelSize])
        out_ras_ds.GetRasterBand(1).SetNoDataValue(ndv)
        gdal.RasterizeLayer(out_ras_ds, [1], vector_ly, burn_values=[1])
        out_ras_arr = out_ras_ds.ReadAsArray()
        vector_ds = None
        # Calculate the indices for the clipped extent of raster array
        x_index = int(round((x_min - x_min_ras) / pixelSize))
        y_index = int(round((y_max_ras - y_max) / pixelSize))
        # Mask input raster with polygon, and export output raster
        raster_out_arr = np.where(out_ras_arr == 1, raster_arr[y_index:y_index + y_res, x_index:x_index + x_res], ndv)
        out_ras_ds.GetRasterBand(1).WriteArray(raster_out_arr)
        out_ras_ds = None

    # Modify the fdr raster, mask it within the watershed extent
    clip_GeoTiff_with_polygon(tempFolder + "/fdr.tif", inputRasterFolder + "/fdr.tif", watershed_uri)
    # Modify the stream raster, mask it within the watershed extent
    clip_GeoTiff_with_polygon(tempFolder + "/stream_out.tif", inputRasterFolder + "/stream_DL.tif", watershed_uri)
    progressBar(progress, label, 80)

    # Convert stream raster to polylines
    def raster_to_polyline(raster_uri, pixelValue, vector_uri):
        raster = gdal.Open(raster_uri)
        srs = raster.GetProjectionRef()

        def pixelOffset2coord(raster_uri, xOffset, yOffset):
            raster = gdal.Open(raster_uri)
            srs = raster.GetProjectionRef()
            geotransform = raster.GetGeoTransform()
            originX = geotransform[0]
            originY = geotransform[3]
            pixelWidth = geotransform[1]
            pixelHeight = geotransform[5]
            coordX = originX + pixelWidth * (xOffset + 0.5)
            coordY = originY + pixelHeight * (yOffset + 0.5)
            return coordX, coordY

        def raster2array(raster_uri):
            raster = gdal.Open(raster_uri)
            array = raster.ReadAsArray()
            return array

        def array2shp(array, vector_uri, raster_uri, pixelValue):
            # max distance between points
            raster = gdal.Open(raster_uri)
            geotransform = raster.GetGeoTransform()
            pixelWidth = geotransform[1]
            maxDistance = math.ceil(math.sqrt(2 * pixelWidth * pixelWidth))
            # array2dict
            count = 0
            roadList = np.where(array == pixelValue)
            multipoint = ogr.Geometry(ogr.wkbMultiLineString)
            pointDict = {}
            for indexY in roadList[0]:
                indexX = roadList[1][count]
                Xcoord, Ycoord = pixelOffset2coord(raster_uri, indexX, indexY)
                pointDict[count] = (Xcoord, Ycoord)
                count += 1
            # dict2wkbMultiLineString
            multiline = ogr.Geometry(ogr.wkbMultiLineString)
            for i in itertools.combinations(pointDict.values(), 2):
                point1 = ogr.Geometry(ogr.wkbPoint)
                point1.AddPoint(i[0][0], i[0][1])
                point2 = ogr.Geometry(ogr.wkbPoint)
                point2.AddPoint(i[1][0], i[1][1])
                distance = point1.Distance(point2)
                if distance < maxDistance:
                    line = ogr.Geometry(ogr.wkbLineString)
                    line.AddPoint(i[0][0], i[0][1])
                    line.AddPoint(i[1][0], i[1][1])
                    multiline.AddGeometry(line)
            # wkbMultiLineString2shp
            shpDriver = ogr.GetDriverByName("ESRI Shapefile")
            if os.path.exists(vector_uri):
                shpDriver.DeleteDataSource(vector_uri)
            outDataSource = shpDriver.CreateDataSource(vector_uri)
            vector_uri = vector_uri.encode('utf-8')
            spatialref = osr.SpatialReference()
            spatialref.ImportFromWkt(srs)
            outLayer = outDataSource.CreateLayer(vector_uri, srs=spatialref, geom_type=ogr.wkbMultiLineString)
            featureDefn = outLayer.GetLayerDefn()
            outFeature = ogr.Feature(featureDefn)
            outFeature.SetGeometry(multiline)
            outLayer.CreateFeature(outFeature)

        array = raster2array(raster_uri)
        array2shp(array, vector_uri, raster_uri, pixelValue)

    raster_to_polyline(inputRasterFolder + "/stream_DL.tif", 1, inputVectorFolder + '/stream_DL.shp')
    progressBar(progress, label, 100)
    # Delete tempFolder and its contents
    # shutil.rmtree(tempFolder)
    global centerlabel
    tkMessageBox._show("Process Completed",
                       "1. Watershed preparation is completed.\n2. Please check watershed and stream features created.\n3. You can adjust str_crt to recreate stream feature, making it more representative to the real flowlines of the watershed.\n4. Total" + str(
                           round((time.time() - start_time), 2)) + " Seconds Taken", icon='info')
    label = Label(frame, text="Process Completed", bg="white").grid(row=rowno, column=1)
    print "Watershed preparation is completed."
    print "Please check watershed and stream features created."
    print "You can adjust str_crt to recreate stream feature, making it more representative to the real flowlines of the watershed."
    print("--- %s seconds ---" % (time.time() - start_time))
    return True


def Untiled_DHM_Function(frame, rowno, inputRasterFolder, inputVectorFolder, outputGdb, outputTxt, tempFolder,
                         outlet_name,
                         fdr_uri, soil_uri, landuse_uri, dem_uri, watershed_uri, stream_uri,
                         sitesDischarge_uri, sitesMoisture_uri, ref_point_uri, landuseFile, soilFile, prcp_File,
                         rainDis12_File, rainDis24_File, tmp_File, RD_d_File, haveDailyPET, PET_method, haveDailyKc,
                         Kc_d_File, cIa_d_File, startDay, endDay, dayRouting, haveDisPrcp=None,
                         DisPrcpFolder=None, PET_File=None, wind_File=None, SSD_File=None,
                         humidity_File=None):
    progress = ttk.Progressbar(frame, orient=HORIZONTAL, length=150, mode='determinate')
    progress.grid(row=rowno + 1, column=1, sticky="W")
    label = Label(frame, bg="White")
    label.grid(row=rowno + 2, column=1, sticky="W")
    progressBar(progress, label, 10)
    tM0 = 50  # Set the watershed average time to drain to field capacity, which determines the rate at which water percolate from upper layer to lower layer, in hours
    soil_f0 = 9.0  # Set the average exponential decline coefficient of hydraulic conductivity with soil depth, in m-1
    k_Sf = 0.3  # Set the adjustment parameter for soilf_f0
    CN_m = 0.692  # Set the modified factor for CN
    c_Ia_m = 1.0  # Set the modified factor for the initial c_Ia
    fc0 = 0.012  # Set constant gravitational infiltration rate, in range 0-1.000
    Kb = 7.0  # Set baseflow storage coefficient, in days
    M_irrg = 0.213  # Set a relative moisture level that below it irrigation will be implemented, (moisture content/Pt)
    # Set irrigation related parameters when irrigation module is active (M_irrg > 0)
    if M_irrg > 0:
        irrg_start = 125  # The start day of irrigation period (in julian day of a year)
        irrg_end = 270  # The end day of irrigation period (in julian day of a year)
        irrgList = ['AGRL']  # The name list of landuse types that needs irrigation
    # Initate some variables
    res = 50.0  # Set the initial water table depth in water bodies, in mm, it should have one digit after decimal point
    TmpSoil = 10.0  # Set the initial soil temperature in degrees Celsius
    # Set other parameters
    Latitude = 31.7  # Set the geographic latitude of the watershed in degrees
    soil_bd = 1.55  # Set the average moist bulk density of soil in Mg per cubic meters
    n_Mnng_streams = 0.04  # Set the Manning's n roughness coefficient for streams/channels
    v_lake = 0.0429  # Set the velocity of water flow in lakes/reservoirs/ponds in meter per second

    """ Set output text file names """
    parameter_Output = "parameters_baseline.txt"  # Set the output file name of parameters
    Qsur_Output = "qOutput_baseline.txt"  # Set the output file name of surface flow at the selected discharge sites
    Qgrd_Output = "bOutput_baseline.txt"  # Set the output file name of ground water flow at the selected discharge sites
    Qrtn_Output = "rOutput_baseline.txt"  # Set the output file name of subsurface return flow at the selected discharge sites
    Qtot_Output = "fOutput_baseline.txt"  # Set the output file name of total streamflow at the selected discharge sites
    M_Output = "MOutput_baseline.txt"  # Set the output file name of moisture content in the unsaturated layer at the monitoring sites
    H_Output = "HOutput_baseline.txt"  # Set the output file name of water table depth at the monitoring sites

    """
    -----------------------------------------------------------------------------------------------------------------
    Above is input of the model, including data and parameters, below is model analysis.
    Generally, there is no need to change the content below, unless modifying the model or do continuous simulation.
    -----------------------------------------------------------------------------------------------------------------
    """

    warnings.filterwarnings("ignore", category=RuntimeWarning)

    """ Define some functions """

    def make_constant_raster_from_base(base_dataset_uri, constant_value, out_uri, out_datatype=None, nodata_value=None):
        """ Create a raster with the same extent, projection with the base raster, but with constant value set by users """
        base_ds = gdal.Open(base_dataset_uri)
        gt_gdal = base_ds.GetGeoTransform()
        prj_gdal = base_ds.GetProjectionRef()
        if out_datatype == None:
            out_datatype = base_ds.GetRasterBand(1).DataType
        out_ds = gdal.GetDriverByName("GTiff").Create(out_uri, base_ds.RasterXSize, base_ds.RasterYSize,
                                                      base_ds.RasterCount, eType=out_datatype)
        out_ds.SetGeoTransform(gt_gdal)
        out_ds.SetProjection(prj_gdal)
        base_arr = base_ds.ReadAsArray()
        ndv = base_ds.GetRasterBand(1).GetNoDataValue()
        if nodata_value == None:
            nodata_value = ndv
        out_arr = np.where(base_arr != ndv, constant_value, nodata_value)
        out_ds.GetRasterBand(1).WriteArray(out_arr)
        out_ds.GetRasterBand(1).SetNoDataValue(nodata_value)
        base_ds = None
        out_ds = None

    def clip_GeoTiff_with_polygon(raster_input_uri, raster_output_uri, polygon_uri):
        """ Clip a GeoTiff raster within the mask of a polygon dataset """
        # Get the information of input raster and polygon
        raster_ds = gdal.Open(raster_input_uri, gdal.GA_ReadOnly)
        raster_arr = raster_ds.ReadAsArray()
        raster_geotransform = raster_ds.GetGeoTransform()
        ndv = raster_ds.GetRasterBand(1).GetNoDataValue()
        raster_datatype = raster_ds.GetRasterBand(1).DataType
        x_min_ras, y_max_ras = raster_geotransform[0], raster_geotransform[3]
        pixelSize = (abs(raster_geotransform[1]) + abs(raster_geotransform[5])) / 2
        vector_ds = ogr.Open(polygon_uri)
        vector_ly = vector_ds.GetLayer(0)
        source_srs = vector_ly.GetSpatialRef()
        x_min, x_max, y_min, y_max = vector_ly.GetExtent()
        x_res = int(round((x_max - x_min) / pixelSize))
        y_res = int(round((y_max - y_min) / pixelSize))
        # Create a output raster from the input polygon
        out_ras_ds = gdal.GetDriverByName("GTiff").Create(raster_output_uri, x_res, y_res, 1, raster_datatype)
        out_ras_ds.SetProjection(source_srs.ExportToWkt())
        out_ras_ds.SetGeoTransform([x_min, pixelSize, 0, y_max, 0, -pixelSize])
        out_ras_ds.GetRasterBand(1).SetNoDataValue(ndv)
        gdal.RasterizeLayer(out_ras_ds, [1], vector_ly, burn_values=[1])
        out_ras_arr = out_ras_ds.ReadAsArray()
        vector_ds = None
        # Calculate the indices for the clipped extent of raster array
        x_index = int(round((x_min - x_min_ras) / pixelSize))
        y_index = int(round((y_max_ras - y_max) / pixelSize))
        # Mask input raster with polygon, and export output raster
        raster_out_arr = np.where(out_ras_arr == 1, raster_arr[y_index:y_index + y_res, x_index:x_index + x_res], ndv)
        out_ras_ds.GetRasterBand(1).WriteArray(raster_out_arr)
        out_ras_ds = None

    def zonal_mean_with_raster(value_raster_input_uri, zones_raster_input_uri):
        """ Calculate zonal mean of value_raster_input_uri within each zones represented by the values of
            the zones_raster_input_uri, ignoring no_data values.
            return a dictionary, with keys representing zone values values representing zonal mean.
            Note: the value_raster_input and the zones_raster_input should be aligned (with the same extent and pixel size)."""
        value_ds = gdal.Open(value_raster_input_uri, gdal.GA_ReadOnly)
        value_arr = value_ds.ReadAsArray()
        ndv_value = value_ds.GetRasterBand(1).GetNoDataValue()
        value_arr = np.where(value_arr == ndv_value, np.NAN, value_arr)
        value_ds = None
        zones_ds = gdal.Open(zones_raster_input_uri, gdal.GA_ReadOnly)
        ndv_zones = zones_ds.GetRasterBand(1).GetNoDataValue()
        zones_arr = zones_ds.ReadAsArray()
        zones_ds = None
        zonal_mean = {}
        for x in range(1, max(map(max, zones_arr)) + 1, 1):  # np.unique(zones_arr):
            if x != ndv_zones:
                current_array = np.where(zones_arr == x, value_arr, np.NAN)
                mean_value = np.nanmean(current_array)
                zonal_mean[x] = mean_value
            else:
                zonal_mean[x] = ndv_value
        return zonal_mean
        # changed the code because during the calculation of WI_arr the keys were not matching as for only 17 values zones were calculated whereas 109 zones were there for keys
        # for x in np.unique(zones_arr):
        #         if x != ndv_zones:
        #                 current_array = np.where(zones_arr == x, value_arr, np.NAN)
        #                 mean_value = np.nanmean(current_array)
        #                 zonal_mean[x] = mean_value
        # return zonal_mean

    def evapotranspiration_FAO_PM(T_max, T_min, altitude, u10, RH_ave, day_of_year, latitude, SSD, albedo=0.23):
        # Calculate parameters from temperature and altitude
        T_mean = (T_max + T_min) / 2
        P = 101.3 * (((293 - 0.0065 * altitude) / 293) ** 5.26)
        pschm_constant = 0.665 * 0.001 * P
        vpc_slope = 4098 * 0.6108 * math.exp(17.27 * T_mean / (T_mean + 237.3)) / ((T_mean + 237.3) ** 2)
        # Calculate vapor pressure deficit:
        e0_max = 0.6108 * math.exp(17.27 * T_max / (T_max + 237.3))
        e0_min = 0.6108 * math.exp(17.27 * T_min / (T_min + 237.3))
        e_sat = (e0_max + e0_min) / 2
        e_act = e_sat * RH_ave / 100.0
        e_deficit = e_sat - e_act
        # Calculate Radiation
        dr = 1 + 0.033 * math.cos(2 * math.pi / 365 * day_of_year)
        sd = 0.409 * math.sin(2 * math.pi / 365 * day_of_year - 1.39)
        ws = math.acos(-math.tan(latitude * math.pi / 180) * math.tan(sd))
        Ra = 24 * 60 / math.pi * 0.0820 * dr * (ws * math.sin(latitude * math.pi / 180) * math.sin(sd) +
                                                math.cos(latitude * math.pi / 180) * math.cos(sd) * math.sin(ws))
        N = 24 / math.pi * ws
        Rs = (0.25 + 0.50 * SSD / N) * Ra
        Rs0 = (0.75 + 0.00002 * altitude) * Ra
        Rns = (1 - albedo) * Rs
        Rs_rate = min(Rs / Rs0, 1.0)
        Rnl = 4.903 * 1e-09 * ((T_max + 273.16) ** 4 + (T_min + 273.16) ** 4) / 2 * (0.34 - 0.14 * (e_act ** 0.5)) * (
                1.35 * Rs_rate - 0.35)
        Rn = Rns - Rnl
        # Convert wind speed from 10m to 2m height
        u2 = u10 * 4.87 / math.log(67.8 * 10.0 - 5.42)
        # Calculate reference evapotranspiration from FAO Penman-Monteith equation
        PET = (0.408 * vpc_slope * Rn + pschm_constant * 900 / (T_mean + 273) * u2 * e_deficit) / (
                vpc_slope + pschm_constant * (1 + 0.34 * u2))
        return PET

    def evapotranspiration_Hargreaves(T_max, T_min, latitude, day_of_year):
        T_mean = (T_max + T_min) / 2
        dr = 1 + 0.033 * math.cos(2 * math.pi / 365 * day_of_year)
        sd = 0.409 * math.sin(2 * math.pi / 365 * day_of_year - 1.39)
        ws = math.acos(-math.tan(latitude * math.pi / 180) * math.tan(sd))
        Ra = 24 * 60 / math.pi * 0.0820 * dr * (ws * math.sin(latitude * math.pi / 180) * math.sin(sd) +
                                                math.cos(latitude * math.pi / 180) * math.cos(sd) * math.sin(ws))
        PET = 0.0023 * (T_mean + 17.8) * ((T_max - T_min) ** 0.5) * Ra / (2.5 - 0.00237 * T_mean)
        return PET

    """Import rasters into numpy array"""
    fdr_ds = gdal.Open(fdr_uri, gdal.GA_ReadOnly)
    fdr_arr = fdr_ds.ReadAsArray()
    ndv_fdr = fdr_ds.GetRasterBand(1).GetNoDataValue()
    # clip the soil and landuse raster data with the delineated watershed from last step "watershed delineation"
    clip_GeoTiff_with_polygon(soil_uri, tempFolder + "/soil.tif", watershed_uri)
    soil_ds = gdal.Open(tempFolder + "/soil.tif", gdal.GA_ReadOnly)
    soil_arr = soil_ds.ReadAsArray()
    soil_ds = None
    clip_GeoTiff_with_polygon(landuse_uri, tempFolder + "/landuse.tif", watershed_uri)
    landuse_ds = gdal.Open(tempFolder + "/landuse.tif", gdal.GA_ReadOnly)
    landuse_arr = landuse_ds.ReadAsArray()
    landuse_ds = None
    if (fdr_arr.shape == landuse_arr.shape == soil_arr.shape) == False:
        print "Warning: the size of input rasters do not match."
    # Aligne fdr, soil, landuse data, in case the fdr data covers more areas
    fdr_arr = np.where(landuse_arr > 0, fdr_arr, ndv_fdr)
    fdr_arr = np.where(soil_arr > 0, fdr_arr, ndv_fdr)
    fdr_ds.GetRasterBand(1).WriteArray(fdr_arr)
    fdr_ds = None
    del fdr_arr

    """ Prepare a zero_raster as a temp to create new rasters """
    make_constant_raster_from_base(fdr_uri, 0.0, outputGdb + "/zero_raster.tif", nodata_value=np.NAN)
    zero_ds = gdal.Open(outputGdb + "/zero_raster.tif", gdal.GA_ReadOnly)
    zero_arr = zero_ds.ReadAsArray()

    # Calculate average altitude of the study area
    clip_GeoTiff_with_polygon(dem_uri, tempFolder + "/dem.tif", watershed_uri)
    dem_ds = gdal.Open(tempFolder + "/dem.tif", gdal.GA_ReadOnly)
    dem_arr = dem_ds.ReadAsArray()
    dem_ds = None
    dem_arr = np.where(zero_arr != 0, np.NAN, dem_arr)
    altitude = np.nanmean(dem_arr)
    del dem_arr
    # os.remove(tempFolder+"/dem.tif")

    """Import landcover and soil data, prepare Manning's n raster, CN raster, Soil_HG raster, soil_z, soil_k, soil_Pe, soil_Pt rasters"""
    soilData = np.genfromtxt(soilFile, skip_header=1,
                             dtype=[('Value', 'i4'), ('HSG', 'i4'), ('soil_z', 'f4'), ('soil_k', 'f4'), ('Pe', 'f4'),
                                    ('Pt', 'f4')])
    soilData.sort(0)
    landuseData = np.genfromtxt(landuseFile, skip_header=1, dtype=[('Value', 'i4'), ('Name', 'a4'), ('Manning_n', 'f4'),
                                                                   ('CN_A', 'f4'), ('CN_B', 'f4'), ('CN_C', 'f4'),
                                                                   ('CN_D', 'f4')])
    landuseData.sort(0)
    # Create soil hydrologic group raster (soilHG)
    soilHG = np.copy(zero_arr)
    for line in soilData:
        soilHG = np.where(soil_arr == int(line['Value']), float(line['HSG']), soilHG)
    del line
    soilHG_ds = gdal.GetDriverByName("GTiff").CreateCopy(outputGdb + "/soil_HG.tif", zero_ds, strict=0)
    soilHG_ds.GetRasterBand(1).WriteArray(soilHG)
    soilHG_ds = None
    # Create soil depth to impervious/restrictive layer raster (soil_z)
    soil_z = np.copy(zero_arr)
    for line in soilData:
        soil_z = np.where(soil_arr == int(line['Value']), float(line['soil_z']), soil_z)
    del line
    soil_z_ds = gdal.GetDriverByName("GTiff").CreateCopy(outputGdb + "/soil_z.tif", zero_ds, strict=0)
    soil_z_ds.GetRasterBand(1).WriteArray(soil_z)
    soil_z_ds = None
    # Create soil hydraulic conductivity raster (soil_k)
    soil_k = np.copy(zero_arr)
    for line in soilData:
        soil_k = np.where(soil_arr == int(line['Value']), float(line['soil_k']), soil_k)
    del line
    soil_k_ds = gdal.GetDriverByName("GTiff").CreateCopy(outputGdb + "/soil_k.tif", zero_ds, strict=0)
    soil_k_ds.GetRasterBand(1).WriteArray(soil_k)
    soil_k_ds = None
    # Create soil effective porosity raster (soil_Pe)
    soil_Pe = np.copy(zero_arr)
    for line in soilData:
        soil_Pe = np.where(soil_arr == int(line['Value']), float(line['Pe']), soil_Pe)
    del line
    soil_Pe_ds = gdal.GetDriverByName("GTiff").CreateCopy(outputGdb + "/soil_Pe.tif", zero_ds, strict=0)
    soil_Pe_ds.GetRasterBand(1).WriteArray(soil_Pe)
    soil_Pe_ds = None
    # Create soil total porosity raster (soil_Pt)
    soil_Pt = np.copy(zero_arr)
    for line in soilData:
        soil_Pt = np.where(soil_arr == int(line['Value']), float(line['Pt']), soil_Pt)
    del line
    soil_Pt_ds = gdal.GetDriverByName("GTiff").CreateCopy(outputGdb + "/soil_Pt.tif", zero_ds, strict=0)
    soil_Pt_ds.GetRasterBand(1).WriteArray(soil_Pt)
    soil_Pt_ds = None
    # Calculate Field Capacity (FC = Pt - Pe)
    soil_FC = (soil_Pt - soil_Pe) / soil_Pt  # in relative volumetric water content
    soil_FC_ave = np.nanmean(soil_FC)
    # Calculate the distributed soil capacity of water, in mm.
    soil_vlm = soil_Pt * soil_z * 1000
    del soil_Pt
    del soil_Pe
    # Create CN2 raster, and a dictionary to pair landuse values and landuse names
    CN2 = np.copy(zero_arr)
    landuseDic = {}
    for line in landuseData:
        CN2 = np.where((landuse_arr == int(line['Value'])) & (soilHG == 1), float(line['CN_A']), CN2)
        CN2 = np.where((landuse_arr == int(line['Value'])) & (soilHG == 2), float(line['CN_B']), CN2)
        CN2 = np.where((landuse_arr == int(line['Value'])) & (soilHG == 3), float(line['CN_C']), CN2)
        CN2 = np.where((landuse_arr == int(line['Value'])) & (soilHG == 4), float(line['CN_D']), CN2)
        landuseDic[line['Name']] = int(line['Value'])
    del line
    CN2 = CN2 * CN_m
    CN2_ds = gdal.GetDriverByName("GTiff").CreateCopy(outputGdb + "/CN2.tif", zero_ds, strict=0)
    CN2_ds.GetRasterBand(1).WriteArray(CN2)
    CN2_ds = None
    del soilHG
    # Prepare numpy arrays with water, residential areas, and irrigated fields representing as 1 and 0 elsewhere
    water = np.where(zero_arr != 0, np.NAN, np.where(landuse_arr == landuseDic['WATR'], 1, 0))
    if M_irrg > 0:
        irrg = np.copy(zero_arr)
        for item in irrgList:
            irrg = np.where(landuse_arr == landuseDic[item], 1, irrg)
        del item
    # Prepare cellSize in meters
    cellSize = (abs(zero_ds.GetGeoTransform()[1]) + abs(zero_ds.GetGeoTransform()[5])) / 2
    # Prepare stream width raster as strWidth, in meter
    str_ds = ogr.Open(stream_uri)
    str_ly = str_ds.GetLayer(0)
    stream_ds = gdal.GetDriverByName("GTiff").CreateCopy(tempFolder + "/strWidth.tif", zero_ds, strict=0)
    # changed this because it wasn't working as the strWidth.tiff was empty and stream_rate=0 and WI_stream was also not work,
    # gdal.RasterizeLayer(stream_ds,[1],str_ly,options=["ATTRIBUTE=strWidth"])
    gdal.RasterizeLayer(stream_ds, [1], str_ly, burn_values=[1])
    strWidth = stream_ds.ReadAsArray()
    stream_ds = None
    # Prepare a numpy array with stream representing as 1 and 0 elsewhere
    stream = np.where(zero_arr != 0, np.NAN, np.where(strWidth != 0, 1, strWidth))
    # Create Manning's n numpy array
    n_Mnng = np.copy(zero_arr)
    for line in landuseData:
        n_Mnng = np.where(landuse_arr == int(line['Value']), float(line['Manning_n']), n_Mnng)
    del line
    n_Mnng = np.where(stream == 1, n_Mnng_streams, n_Mnng)

    del soilData
    del landuseData

    """Import climate data"""
    # Get daily rainfall data from prcp_d.txt file
    prcp_d = pd.read_csv(prcp_File, sep='\t', header=0, index_col=0, squeeze=True, parse_dates=True)
    # Get rainfall distribution data from 12raindis.txt and 24raindis.txt
    rainDis12 = pd.read_csv(rainDis12_File, sep='\t', header=0, index_col=0, squeeze=True)
    rainDis24 = pd.read_csv(rainDis24_File, sep='\t', header=0, index_col=0, squeeze=True)
    # Get daily temperature data from tmp_d.txt file
    tmp_d = pd.read_csv(tmp_File, sep='\t', header=0, index_col=0, parse_dates=True,
                        usecols=['date', 'TEM_max', 'TEM_min'], na_values=-99.9)
    tmp_d.fillna(tmp_d.rolling(7, min_periods=1, center=True).mean(), inplace=True)  # Fill with 7-day average values
    tmp_d.ffill(inplace=True)  # fill forward
    tmp_d.bfill(inplace=True)  # fill backward
    tmp_d['TEM_mean'] = (tmp_d.TEM_max + tmp_d.TEM_min) / 2
    TmpAirAn = tmp_d.TEM_mean.resample('A').mean()[tmp_d.TEM_mean.resample('A').count() > 350].mean()
    # if daily PET data is available, get daily PET data from PET_d.txt file
    if haveDailyPET == True:
        PET_d = pd.read_csv(PET_File, sep='\t', header=0, index_col=0, squeeze=True, parse_dates=True, na_values=-6999)
    # If PET method is FAO Penman-Monteith, get daily climate data needed (wind, sunshine duration, relative humidity)
    elif PET_method == 2:
        win_df = pd.read_csv(wind_File, sep='\t', header=0, index_col=0, parse_dates=True,
                             usecols=['date', 'WIN_ave'], na_values=-99.9)
        win_df.fillna(win_df.rolling(7, min_periods=1, center=True).mean(),
                      inplace=True)  # Fill with 7-day average values
        win_df.ffill(inplace=True)
        win_df.bfill(inplace=True)
        rh_df = pd.read_csv(humidity_File, sep='\t', header=0, index_col=0, parse_dates=True,
                            usecols=['date', 'RHU_ave'], na_values=-99)
        rh_df.fillna(rh_df.rolling(7, min_periods=1, center=True).mean(),
                     inplace=True)  # Fill with 7-day average values
        rh_df.ffill(inplace=True)
        rh_df.bfill(inplace=True)
        ssd_df = pd.read_csv(SSD_File, sep='\t', header=0, index_col=0, parse_dates=True,
                             usecols=['date', 'SSD'], na_values=-99.9)
        ssd_df.fillna(ssd_df.rolling(7, min_periods=1, center=True).mean(),
                      inplace=True)  # Fill with 7-day average values
        ssd_df.ffill(inplace=True)
        ssd_df.bfill(inplace=True)
    # if daily Kc data is available, get daily Kc data from Kc_d.txt file
    if haveDailyKc == True:
        Kc_d = pd.read_csv(Kc_d_File, sep='\t', header=0, index_col=0)
    # Get daily root depth data from RD_d.txt file
    RD_d = pd.read_csv(RD_d_File, sep='\t', header=0, index_col=0)
    # Get daily c_Ia parameter value from cIa_d.txt file
    cIa_d = pd.read_csv(cIa_d_File, sep='\t', header=0, index_col=0, squeeze=True)

    """Prepare some common variables"""
    # Prepare pandas dates for the simulation period
    dates = pd.date_range(startDay, endDay, None, 'D')
    # Calculate maximum damping depth of soil, in mm
    dd_mx = 1000 + 2500 * soil_bd / (soil_bd + 686 * math.exp(-5.63 * soil_bd))
    # Read X and Y coordinates of discharge sites and moisture sites in dictionaries,
    # and create a dictionary (outlets_dic) to store each discharge site in a seperate vector.
    # Discharge sites
    discharge_ds = ogr.Open(sitesDischarge_uri, False)
    discharge_ly = discharge_ds.GetLayer(0)
    srs = discharge_ly.GetSpatialRef()
    discharge_ly.ResetReading()
    discharge_defn = discharge_ly.GetLayerDefn()
    discharge_fieldlist = []
    for i in range(discharge_defn.GetFieldCount()):
        discharge_fieldlist += [discharge_defn.GetFieldDefn(i).GetName()]
    discharge_dic = {}
    outlets_dic = {}
    for feature in discharge_ly:
        if feature is not None:
            feature_name = feature.GetField(discharge_fieldlist.index('Name'))
            geom = feature.GetGeometryRef()
            feature_XY = [geom.GetX(), geom.GetY()]
            discharge_dic[feature_name] = feature_XY
            if os.path.exists(tempFolder + "/outlet" + str(feature_name) + ".shp"):
                ogr.GetDriverByName('ESRI Shapefile').DeleteDataSource(
                    tempFolder + "/outlet" + str(feature_name) + ".shp")
            outletds = ogr.GetDriverByName('ESRI Shapefile').CreateDataSource(
                tempFolder + "/outlet" + str(feature_name) + ".shp")
            tempShapeEncode = (tempFolder + "/outlet" + str(feature_name) + ".shp").encode('utf-8')
            outletly = outletds.CreateLayer(tempShapeEncode, srs=srs, geom_type=ogr.wkbPoint)
            outletDefn = outletly.GetLayerDefn()
            outFeature = ogr.Feature(outletDefn)
            outFeature.SetGeometry(geom)
            outletly.CreateFeature(outFeature)
            outFeature.Destroy()
            outletds = None
            outlets_dic[feature_name] = tempFolder + "/outlet" + str(feature_name) + ".shp"
    discharge_ds = None
    del srs
    del discharge_fieldlist
    del feature
    del feature_name
    del geom
    del feature_XY
    del outFeature
    del outletly
    del outletds
    del outletDefn
    # Moisture sites
    moisture_ds = ogr.Open(sitesMoisture_uri, False)
    moisture_ly = moisture_ds.GetLayer(0)
    moisture_ly.ResetReading()
    moisture_defn = moisture_ly.GetLayerDefn()
    moisture_fieldlist = []
    for i in range(moisture_defn.GetFieldCount()):
        moisture_fieldlist += [moisture_defn.GetFieldDefn(i).GetName()]
    moisture_dic = {}
    for feature in moisture_ly:
        if feature is not None:
            feature_name = feature.GetField(moisture_fieldlist.index('Name'))
            geom = feature.GetGeometryRef()
            feature_XY = [geom.GetX(), geom.GetY()]
            feature_landuse = feature.GetField(moisture_fieldlist.index('landuse'))
            feature_soil = feature.GetField(moisture_fieldlist.index('soil'))
            moisture_dic[feature_name] = [feature_XY, feature_landuse, feature_soil]
    moisture_ds = None
    del moisture_fieldlist
    del feature
    del feature_name
    del geom
    del feature_XY
    del feature_landuse
    del feature_soil
    # Convert X and Y coordinates of discharge and moisture sites into row and column indices of rasters
    originX = zero_ds.GetGeoTransform()[0]
    originY = zero_ds.GetGeoTransform()[3]
    pixelWidth = zero_ds.GetGeoTransform()[1]
    pixelHeight = zero_ds.GetGeoTransform()[5]
    # Discharge sites "look at lines 452 and 492"
    for (key, value) in discharge_dic.items():
        X_index = int(math.floor((value[0] - originX) / pixelWidth))
        Y_index = int(math.floor((value[1] - originY) / pixelHeight))
        discharge_dic[key] = [Y_index, X_index]
    del key
    del value
    del X_index
    del Y_index
    # Moisture sites
    for (key, value) in moisture_dic.items():
        X_index = int(math.floor((value[0][0] - originX) / pixelWidth))
        Y_index = int(math.floor((value[0][1] - originY) / pixelHeight))
        moisture_dic[key][0] = [Y_index, X_index]
    del key
    del value
    del X_index
    del Y_index
    # Modify landuse and soil arrays with the known data from moisture sites
    for (key, value) in moisture_dic.items():
        landuse_arr[value[0][0], value[0][1]] = value[1]
        soil_arr[value[0][0], value[0][1]] = value[2]
    del key
    del value
    del soil_arr
    # Prepare outlet_ras raster (rasterized outlet site data) for distance_to_stream analysis
    make_constant_raster_from_base(fdr_uri, 0, outputGdb + "/outlet_ras.tif", out_datatype=gdal.GDT_Byte,
                                   nodata_value=255)
    outlet_ras_ds = gdal.Open(outputGdb + "/outlet_ras.tif", gdal.GA_Update)
    outlet_ras = outlet_ras_ds.ReadAsArray()
    outlet_ras[discharge_dic[outlet_name][0], discharge_dic[outlet_name][1]] = 1
    outlet_ras_ds.GetRasterBand(1).WriteArray(outlet_ras)
    outlet_ras_ds = None
    del outlet_ras
    # Generate a list of subwatershed raster arrays with given monitoring gauges
    subwtshd_dic = {}
    routing.routing_core.calculate_flow_weights(fdr_uri, tempFolder + "/outflow_weights.tif",
                                                tempFolder + "/outflow_dir.tif")
    for (key, value) in outlets_dic.items():
        routing.routing_core.delineate_watershed(tempFolder + "/outflow_dir.tif", tempFolder + "/outflow_weights.tif",
                                                 value, 0,
                                                 inputRasterFolder + "/stream_DL.tif",
                                                 tempFolder + "/watershed_" + str(key) + ".shp",
                                                 tempFolder + "/Moutlet" + key + ".shp")
        wtshd_ds = ogr.Open(tempFolder + "/watershed_" + str(key) + ".shp", False)
        wtshd_ly = wtshd_ds.GetLayer(0)
        make_constant_raster_from_base(fdr_uri, 0, tempFolder + "/wtshd_" + str(key) + ".tif",
                                       out_datatype=gdal.GDT_Byte, nodata_value=0)
        # changed nodata value to 0 beacuse 255 was not visible and it won't affect anyway
        wtshd_raster_ds = gdal.Open(tempFolder + "/wtshd_" + str(key) + ".tif", gdal.GA_Update)
        gdal.RasterizeLayer(wtshd_raster_ds, [1], wtshd_ly, burn_values=[1])
        wtshd_arr = wtshd_raster_ds.ReadAsArray()
        wtshd_raster_ds = None
        wtshd_ds = None
        subwtshd_dic[key] = wtshd_arr
        # os.remove(tempFolder+"/wtshd_"+str(key)+".tif")
        # ogr.GetDriverByName("ESRI Shapefile").DeleteDataSource(tempFolder+"/Moutlet"+str(key)+".shp")
    del key
    del value
    del outlets_dic
    # Generate a list of the areas for each subwatersheds with monitoring gauges, in square meters
    temp_arr = np.where(zero_arr == 0, 1, 0)
    area_tot = (np.count_nonzero(temp_arr)) * (cellSize ** 2)
    del temp_arr
    area_subs = {}
    for (key, value) in subwtshd_dic.items():
        temp = np.where(value == 1, 1, 0)
        area_subs[key] = np.count_nonzero(temp) * (cellSize ** 2)
        del temp
    del key
    del value
    # Calculate ground flow routing parameters
    g0 = 1 / Kb / (2 + 1 / Kb)
    g1 = g0
    g2 = (2 - 1 / Kb) / (2 + 1 / Kb)
    # Calculate the area rate of streams
    stream_rate = np.where(stream == 1, strWidth / cellSize, np.where(stream == 0, 0, np.NAN))
    rate_stream = np.nanmean(stream_rate)
    del stream_rate
    # Calculate the area rate of water bodies (including lakes/ponds/reservoirs/streams
    rate_water = np.nanmean(water) + rate_stream

    """ Prepare the output files """
    # Writh the head of average c_Ia, ET, Fc, M and TmpSoil values of simulating days
    parameters = open(outputTxt + '/' + parameter_Output, 'a')
    parameters.write(
        'The average c_Ia, ET, Fc, M_relative and TmpSoil values are estimated by DHM-WM global water balance routine as below:\n')
    parameters.write('date\tc_Ia\tET(mm)\tFc(mm)\tM_rel\tTmpSoil(C)\n')
    # Write the head of output surface flow
    qOutput = open(outputTxt + '/' + Qsur_Output, 'a')
    qOutput.write(
        'The surface flow (cms) at the sub/watershed outlet(s) is simulated by DHM-WM global water balance routine as below:\n')
    qOutput.write('date\t')
    for key in discharge_dic.keys():
        qOutput.write(str(key) + '\t')
    qOutput.seek(-1, 1)
    qOutput.truncate()
    qOutput.write('\n')
    del key
    # Write the head of output total streamflow
    fOutput = open(outputTxt + '/' + Qtot_Output, 'a')
    fOutput.write(
        'The total streamflow (cms) at the sub/watershed outlet(s) is simulated by DHM-WM global water balance routine as below:\n')
    fOutput.write('date\t')
    for key in discharge_dic.keys():
        fOutput.write(str(key) + '\t')
    fOutput.seek(-1, 1)
    fOutput.truncate()
    fOutput.write('\n')
    del key
    # Set the output file name of return flow
    rFlow_File = outputTxt + '/' + Qrtn_Output
    rOutput = open(rFlow_File, 'w')
    rOutput.write(
        'The subsurface return flow (cms) at the sub/watershed outlet(s) is simulated by DHM-WM global water balance routine as below:\n')
    rOutput.close()
    del rOutput
    # Set the output file name of base flow
    bFlow_File = outputTxt + '/' + Qgrd_Output
    bOutput = open(bFlow_File, 'w')
    bOutput.write(
        'The groundwater flow (cms) at the sub/watershed outlet(s) is simulated by DHM-WM global water balance routine as below:\n')
    bOutput.close()
    del bOutput
    # Set the output file name of moisture content in the unsaturated layer at the monitoring sites
    M_File = outputTxt + '/' + M_Output
    MOutput = open(M_File, 'w')
    MOutput.write(
        'The relative moisture content (unitless) in the unsaturated layer at the selected moisutre sites is simulated by DHM-WM global water balance routine as below:\n')
    MOutput.close()
    del MOutput
    # Set the output file name of water table depth at the monitoring sites
    H_File = outputTxt + '/' + H_Output
    HOutput = open(H_File, 'w')
    HOutput.write(
        'The subsurface water table depth (m) at the selected moisture sites is simulated by DHM-WM global water balance routine as below:\n')
    HOutput.close()
    del HOutput

    """Prepare some common rasters"""
    # Set the used Fc0
    Fc0_normal = fc0 * soil_k * 1000 / 24  # in mm/hr
    Fc0_winter = 0.1 * Fc0_normal  # Assume 0.1 times of gravitational infiltration during days when surface soil becomes frozen
    # Prepare reference zone raster
    # Step 1. Get X and Y coordinates of reference points
    ref_point_ds = ogr.Open(ref_point_uri, False)
    ref_point_ly = ref_point_ds.GetLayer(0)
    ref_point_ly.ResetReading()
    ref_point_defn = ref_point_ly.GetLayerDefn()
    ref_point_fieldlist = []
    for i in range(ref_point_defn.GetFieldCount()):
        ref_point_fieldlist += [ref_point_defn.GetFieldDefn(i).GetName()]
    ref_point_dic = {}
    for feature in ref_point_ly:
        if feature is not None:
            feature_name = feature.GetField(ref_point_fieldlist.index('Id'))
            geom = feature.GetGeometryRef()
            feature_XY = [geom.GetX(), geom.GetY()]
            ref_point_dic[feature_name] = feature_XY
    ref_point_ds = None
    del ref_point_fieldlist
    del feature
    del feature_name
    del geom
    del feature_XY
    for (key, value) in ref_point_dic.items():
        X_index = int(math.floor((value[0] - originX) / pixelWidth))
        Y_index = int(math.floor((value[1] - originY) / pixelHeight))
        ref_point_dic[key] = [Y_index, X_index]
    del key
    del value
    del X_index
    del Y_index
    # Step 2. Change the flow direction at the sites of reference points to no data
    fdr_ds = gdal.Open(fdr_uri, gdal.GA_ReadOnly)
    fdr_ref_ds = gdal.GetDriverByName("GTiff").CreateCopy(tempFolder + "/fdr_ref.tif", fdr_ds, strict=0)
    fdr_ref_arr = fdr_ref_ds.ReadAsArray()
    for value in ref_point_dic.values():
        fdr_ref_arr[value[0], value[1]] = ndv_fdr
    del value
    fdr_ref_ds.GetRasterBand(1).WriteArray(fdr_ref_arr)
    fdr_ref_ds = None
    del fdr_ref_arr
    # Change the flow direction at the outlet to no_data value for flow_accumulation analysis
    fdr_m_ds = gdal.GetDriverByName("GTiff").CreateCopy(tempFolder + "/fdr_m.tif", fdr_ds, strict=0)
    fdr_m_arr = fdr_m_ds.ReadAsArray()
    fdr_m_arr[discharge_dic[outlet_name][0], discharge_dic[outlet_name][1]] = ndv_fdr
    fdr_m_ds.GetRasterBand(1).WriteArray(fdr_m_arr)
    fdr_m_ds = None
    del fdr_m_arr
    fdr_ds = None
    # Step 3. Do watershed delineation for each reference point
    routing.routing_core.calculate_flow_weights(tempFolder + "/fdr_ref.tif", tempFolder + "/outflow_weights1.tif",
                                                tempFolder + "/outflow_dir1.tif")
    routing.routing_core.delineate_watershed(tempFolder + "/outflow_dir1.tif", tempFolder + "/outflow_weights1.tif",
                                             ref_point_uri,
                                             0, inputRasterFolder + "/stream_DL.tif", tempFolder + "/ref_zones.shp",
                                             tempFolder + "/M_ref_points.shp")
    # ogr.GetDriverByName("ESRI Shapefile").DeleteDataSource(tempFolder+"/M_ref_points.shp")
    # os.remove(tempFolder+"/outflow_weights1.tif")
    # os.remove(tempFolder+"/outflow_dir1.tif")

    # Step 4. Convert the delineated reference zones shapefile to raster, read in numpy array;
    # and create a shapefile representing reference zones
    ref_zone_ds = ogr.Open(tempFolder + "/ref_zones.shp", False)
    ref_zone_ly = ref_zone_ds.GetLayer(0)
    make_constant_raster_from_base(fdr_uri, -99, tempFolder + "/ref_zones.tif", out_datatype=gdal.GDT_Int16,
                                   nodata_value=-99)
    ref_zone_raster_ds = gdal.Open(tempFolder + "/ref_zones.tif", gdal.GA_Update)
    gdal.RasterizeLayer(ref_zone_raster_ds, [1], ref_zone_ly, options=["ATTRIBUTE=Id"])
    ref_zones = ref_zone_raster_ds.ReadAsArray()
    ref_zone_raster_ds = None
    ref_zone_ds = None

    # Prepare slope raster
    slp_ds = gdal.DEMProcessing(tempFolder + "/slp.tif", dem_uri, "slope", slopeFormat="percent")
    slp_ds = None
    clip_GeoTiff_with_polygon(tempFolder + "/slp.tif", tempFolder + "/slp1.tif", watershed_uri)
    slp_ds = gdal.Open(tempFolder + "/slp1.tif", gdal.GA_ReadOnly)
    slp_arr = slp_ds.ReadAsArray()
    slp_v = np.where(slp_arr < 0, np.NAN, np.where((slp_arr < 0.5) | (water == 1), 0.005, slp_arr / 100))
    slp_ds = None
    del slp_arr
    # os.remove(tempFolder+"/slp.tif")
    # os.remove(tempFolder+"/slp1.tif")

    # Calculate the wetness index, STI
    routing.flow_accumulation(tempFolder + "/fdr_ref.tif", fdr_uri, tempFolder + "/fac_ref.tif")
    fac_ref_ds = gdal.Open(tempFolder + "/fac_ref.tif", gdal.GA_ReadOnly)
    fac_ref_arr = fac_ref_ds.ReadAsArray()
    fac_ref_ds = None
    WI_arr = np.log(fac_ref_arr * cellSize / (soil_k * soil_z * slp_v))
    WI_stream = np.where(stream == 1, WI_arr, np.NAN)
    WI_stream_ds = gdal.GetDriverByName("GTiff").CreateCopy(tempFolder + "/WI_stream.tif", zero_ds, strict=0)
    WI_stream_ds.GetRasterBand(1).WriteArray(WI_stream)
    WI_stream_ds = None
    WI_stream_stats = zonal_mean_with_raster(tempFolder + "/WI_stream.tif", tempFolder + "/ref_zones.tif")

    for key in ref_point_dic.keys():
        WI_arr = np.where((stream == 1) & (ref_zones == key), WI_stream_stats[key], WI_arr)
    del key
    WI_ds = gdal.GetDriverByName("GTiff").CreateCopy(outputGdb + "/STI.tif", zero_ds, strict=0)
    WI_ds.GetRasterBand(1).WriteArray(WI_arr)
    WI_ds = None
    # os.remove(tempFolder+"/WI_stream.tif")
    # os.remove(tempFolder+"/fac_ref.tif")
    del WI_stream_stats
    # Set the reference Wetness Index (water table) for each parts of the reference zones, STI_ref
    WI_wtr = np.where((water == 1) | (stream == 1), WI_arr, np.NAN)
    WI_wtr_ds = gdal.GetDriverByName("GTiff").CreateCopy(tempFolder + "/WI_wtr.tif", zero_ds, strict=0)
    WI_wtr_ds.GetRasterBand(1).WriteArray(WI_wtr)
    WI_wtr_ds = None
    WI_wtr_stats = zonal_mean_with_raster(tempFolder + "/WI_wtr.tif", tempFolder + "/ref_zones.tif")
    WI_ref = np.copy(zero_arr)
    for key in ref_point_dic.keys():
        WI_ref = np.where(ref_zones == key, WI_wtr_stats[key], WI_ref)
    del key
    WI_ref_ds = gdal.GetDriverByName("GTiff").CreateCopy(outputGdb + "/STI_ref.tif", zero_ds, strict=0)
    WI_ref_ds.GetRasterBand(1).WriteArray(WI_ref)
    WI_ref_ds = None
    # os.remove(tempFolder+"/WI_wtr.tif")
    del WI_wtr_stats
    # Prepare the relative STI raster in a variable named "WI_rel"
    WI_rel = WI_ref - WI_arr
    WI_rel_ds = gdal.GetDriverByName("GTiff").CreateCopy(outputGdb + "/STI_rel.tif", zero_ds, strict=0)
    WI_rel_ds.GetRasterBand(1).WriteArray(WI_rel)
    WI_rel_ds = None
    del WI_arr
    del WI_ref
    del fac_ref_arr
    del ref_zones
    del WI_stream
    del WI_wtr
    del soil_k

    # Prepare absolute retention parameter raster (S_abs_mx, here named S1)
    S2 = 25400 / CN2 - 254
    S1 = 2.281 * S2  # Set the absolute S (S_abs_mx)
    S1_ds = gdal.GetDriverByName("GTiff").CreateCopy(outputGdb + "/S_abs_mx.tif", zero_ds, strict=0)
    S1_ds.GetRasterBand(1).WriteArray(S1)
    S1_ds = None
    del S2
    del CN2

    # Calculate distributed tM (time to drain to field capacity for moisture update in the upper layer) according to wetness index
    tM = np.where(zero_arr != 0, np.NAN, np.where(WI_rel > 0, tM0 * (np.nanmean(WI_rel)) / WI_rel, 1))
    M_loss = 1 - np.exp(-24 / tM)  # Calculate the distributed moisture loss velocity
    del tM
    # Calculate the H_temp for very wet days
    soil_f = soil_f0 * (1 + k_Sf)
    H_temp = np.where(zero_arr != 0, np.NAN, np.where(WI_rel >= 0, 0.001 + WI_rel / soil_f, 0.001))
    H_temp = np.fmin(H_temp, soil_z)
    del soil_f

    # Prepare grid cell flow length array for travel time calculation
    outflow_weight_ds = gdal.Open(tempFolder + "/outflow_weights.tif", gdal.GA_ReadOnly)
    outflow_weight = outflow_weight_ds.ReadAsArray()
    outflow_weight_ds = None
    outflow_dir_ds = gdal.Open(tempFolder + "/outflow_dir.tif", gdal.GA_ReadOnly)
    outflow_dir = outflow_dir_ds.ReadAsArray()
    outflow_dir_ds = None
    length1 = np.where(zero_arr != 0, np.NAN, np.where((outflow_dir % 2) == 1, 1.41421356237 * cellSize, cellSize))
    outflow_dir2 = np.where(zero_arr != 0, np.NAN, (outflow_dir + 1) % 8)
    length2 = np.where(zero_arr != 0, np.NAN, np.where((outflow_dir2 % 2) == 1, 1.41421356237 * cellSize, cellSize))
    length = length1 * outflow_weight + length2 * (1 - outflow_weight)
    del length1
    del length2
    del outflow_dir2
    del outflow_weight
    del outflow_dir
    # os.remove(tempFolder+"/outflow_weights.tif")
    # os.remove(tempFolder+"/outflow_dir.tif")
    length_ds = gdal.GetDriverByName("GTiff").CreateCopy(tempFolder + "/length.tif", zero_ds, strict=0)
    length_ds.GetRasterBand(1).WriteArray(length)

    length_ds = None

    """Initiate some variables and rasters"""
    # Create a dictionary to store bOp values (in cms) for the current simulating day, and initiate it
    bOp = {}
    for (key, value) in area_subs.items():
        bOp[key] = 0.005 * value / 1000000
    del key
    del value
    # Initiate a dictionary to store Fc_ave (in mm) for each subwatersheds
    FcAve_dic = {}
    for key in area_subs.keys():
        FcAve_dic[key] = 0.0
    del key
    # Set the initial raster for moisture in the saturated layer, according to the initial water table depth, res
    H_bal = np.where(zero_arr != 0, np.NAN, np.where(WI_rel >= 0, res / 1000 + WI_rel / soil_f0, res / 1000))
    if res == 0:
        H_bal = np.fmax(H_bal, H_temp)
    H_bal = np.fmin(H_bal, soil_z)
    M_bal = (1 - H_bal / soil_z) * S1
    # Set the initial absolute S values, only unsaturated soil is accounted
    S_abs = S1 - M_bal
    # Set the initial moisture content of the whole soil profile
    M_next = M_bal + 0.5 * S_abs
    # Set the initial raster for moisture content in the unsaturated layer
    M = 0.5 * S_abs
    # Set the initial S values for the unsaturated layer
    S = S_abs - M
    # Set the initial relative moisture content for the unsaturated layer
    M_dis = M / S_abs
    qm_ds = None

    """ Create some pandas DataFrame to store simulation results """
    # Create a pandas DataFrame to store bOp values
    bOpArr = pd.DataFrame(np.zeros((len(dates), len(discharge_dic)), dtype=np.float32), dates,
                          columns=discharge_dic.keys())
    bOpArr_adj = pd.DataFrame(np.zeros((len(dates), len(discharge_dic)), dtype=np.float32), dates,
                              columns=discharge_dic.keys())
    # Create a pandas DataFrame to store rOp values
    rOpArr = pd.DataFrame(np.zeros((len(dates), len(discharge_dic)), dtype=np.float32), dates,
                          columns=discharge_dic.keys())
    # Create a pandas DataFrame to store sample M values at moisture monitoring sites
    MArr = pd.DataFrame(np.zeros((len(dates), len(moisture_dic)), dtype=np.float32), dates, columns=moisture_dic.keys())
    # Create a pandas DataFrame to store sample H values at moisture monitoring sites
    HArr = pd.DataFrame(np.zeros((len(dates), len(moisture_dic)), dtype=np.float32), dates, columns=moisture_dic.keys())

    """ DHM-WM global water balance routine starts simulation """
    date_n = 0
    progressBar(progress, label, 10)
    progressCheck = 10.0
    while date_n < len(dates):
        progressCheck = round(progressCheck + 40.0 / len(dates), 2)
        progressBar(progress, label, progressCheck)

        # Prepare a string of the simulateion date, and day of year
        date = str(dates[date_n].year * 10000 + dates[date_n].month * 100 + dates[date_n].day)
        day = dates[date_n].dayofyear

        # Calculate the baseflow routing
        for (key, value) in FcAve_dic.items():
            bOp[key] = (g0 + g1) * value * area_subs[key] / 1000 / 3600 / 24 + g2 * bOp[key]
            bOpArr.loc[date, key] = bOp[key]  # Store the baseflow results into pandas DataFrame
        del key
        del value

        # Update S values as S = S_abs - M, modify S values in water bodies
        S = np.where(water == 1, 0, S_abs - M)

        # Calculate the average soil temperature of the day in 500mm depth, as a representation of soil temperature
        # Calculate damping depth in mm
        dd_factor = np.nanmean(M_next) / ((0.356 - 0.144 * soil_bd) * (np.nanmean(S1)))
        dd = dd_mx * math.exp(math.log(500 / dd_mx) * (((1 - dd_factor) / (1 + dd_factor)) ** 2))
        del dd_factor
        # Calculate df
        zd = 500 / dd
        df = zd / (zd + math.exp(-0.867 - 2.078 * zd))
        del zd
        # Calculate soil temperature, assuming soil surface temperature is 1 degree lower than the average air temperature
        TmpSoil = 0.8 * TmpSoil + 0.2 * (
                df * (TmpAirAn - tmp_d.loc[date, 'TEM_mean'] - 1) + tmp_d.loc[date, 'TEM_mean'] - 1)
        del df

        # Use Mishra-Singh CN method to calculate infiltration-excess runoff and relative variables
        if prcp_d.loc[date] > 0:
            # Prepare precipitation data first, use distributed data if available, or use the number in prcp_d.txt file
            if haveDisPrcp == True:
                prcp_ds = gdal.Open(DisPrcpFolder + 'prcp' + date + '.tif', gdal.GA_ReadOnly)
                prcp = prcp_ds.ReadAsArray()
                prcp_ds = None
            else:
                prcp = prcp_d.loc[date]
            # Prepare c_Ia
            c_Ia = c_Ia_m * cIa_d.loc[day] * S / S_abs
            c_Ia_ave = np.nanmean(c_Ia)
            # Estimate the duration of runoff using synthetic rainfall distribution curve
            tGen = np.where(zero_arr == 0, 0.5, np.NAN)
            if prcp_d.loc[
                date] < 50:  # Use 12-h synthetic rainfall distribution curve when daily precipitation is smaller than 50 mm
                for i in rainDis12.index[:-1]:
                    tGen = np.where((c_Ia * S < rainDis12.loc[i + 0.5] * prcp) & (c_Ia * S >= rainDis12[i] * prcp),
                                    12 - i, tGen)
                del i
            else:  # Use 24-h synthetic rainfall distribution curve when daily precipitation is larger than 50 mm
                for i in rainDis24.index[:-1]:
                    tGen = np.where((c_Ia * S < rainDis24[i + 0.5] * prcp) & (c_Ia * S >= rainDis24[i] * prcp), 24 - i,
                                    tGen)
                del i
            # Set actual Fc0 according to soil temperature and runoff generation time
            if TmpSoil < 0:
                Fc0 = Fc0_winter * tGen
            else:
                Fc0 = Fc0_normal * tGen
            # Calculate direct surface runoff with general Mishra-Singh model
            q = np.where(zero_arr != 0, np.NAN, np.where((c_Ia * S + Fc0) <= prcp,
                                                         (prcp - c_Ia * S - Fc0) * (prcp - c_Ia * S - Fc0 + M) / (
                                                                 prcp - c_Ia * S - Fc0 + M + S), 0))
            q = np.where(water == 1, 0, q)
            # Calculate gravitational infiltration Fc
            Fc = np.where(zero_arr != 0, np.NAN,
                          np.where((c_Ia * S + Fc0) <= prcp, Fc0, np.where((c_Ia * S) <= prcp, prcp - c_Ia * S, 0)))
            # Calculate dynamic infiltration Fd with soil moisture budgeting equation
            Fd = np.where(zero_arr != 0, np.NAN, np.where((c_Ia * S + Fc0) <= prcp, prcp - c_Ia * S - Fc - q, 0))
            # Calculate initial abstraction
            Ia = np.where(zero_arr != 0, np.NAN, np.where((c_Ia * S) <= prcp, c_Ia * S, prcp))
        else:
            c_Ia_ave = 0
            Fd_m = 0
            Fc_ave = 0
            for key in area_subs.keys():
                FcAve_dic[key] = 0.0
            del key

        # Calculate evapotranspiration ET
        # Determine the potential ET (PET)
        if haveDailyPET == False:  # if PET data is unavaiable, calculate PET using 1. Hargreaves method or 2. Panmen-Monteith method.
            if PET_method == 1:
                E = evapotranspiration_Hargreaves(tmp_d.loc[date, 'TEM_max'], tmp_d.loc[date, 'TEM_min'], Latitude, day)
            elif PET_method == 2:
                E = evapotranspiration_FAO_PM(tmp_d.loc[date, 'TEM_max'], tmp_d.loc[date, 'TEM_min'], altitude,
                                              win_df.loc[date, 'WIN_ave'],
                                              rh_df.loc[date, 'RHU_ave'], day, Latitude, ssd_df.loc[date, 'SSD'],
                                              albedo=0.23)
        elif date in PET_d.dropna().index:  # If PET data is available, use it directly
            E = PET_d[date]
        else:  # if the PET data in the simulation day is missing, calculate PET using Hargreaves method instead
            E = evapotranspiration_Hargreaves(tmp_d.loc[date, 'TEM_max'], tmp_d.loc[date, 'TEM_min'], Latitude, day)
        if E <= 0.0:
            E = 0.0
        if haveDailyKc == True:  # if daily Kc is available, adjust PET for different land cover and different day
            PET = E
            for x in Kc_d.columns:
                PET = np.where(landuse_arr == int(x), Kc_d.loc[day, x] * E, PET)
            del x
        else:
            PET = E

        # Incorporate c_Ia into water budget
        if prcp_d.loc[date] > 0:
            # Adjust Fc for water areas
            if (haveDisPrcp == True) | (haveDailyKc == True):
                Fc = np.where((water == 1) & (Fc < (prcp - PET)), Fc,
                              np.where((water == 1) & ((prcp - PET) > 0), prcp - PET, np.where(water == 1, 0, Fc)))
            else:
                Fc = np.where((water == 1) & (Fc < (prcp - PET)), Fc, np.where(water == 1, max(prcp - PET, 0), Fc))
            Fc_ave = np.nanmean(Fc)
            # Prepare FcAve_dic for base flow estimation on next simulation day
            for (key, value) in subwtshd_dic.items():
                current_array = np.where(value == 1, Fc, np.NAN)
                FcAve_dic[key] = np.nanmean(current_array)
                del current_array
            del key
            del value
            # Calculate ET from canopy interception (assume to be half of the Ia)
            F_Ia = np.where(zero_arr != 0, np.NAN, np.where(0.5 * Ia > PET, Ia - PET, 0.5 * Ia))
            ET_can = np.where(zero_arr != 0, np.NAN, np.where(0.5 * Ia > PET, PET, 0.5 * Ia))
            PET_soil = PET - ET_can  # Calculate PET from the soil profile
            # Adjust surface runoff (q to qm) and dynamic infiltration (Fd to Fd_m) accounting for actual water balance using M_next
            Fd_m = np.where(zero_arr != 0, np.NAN, np.where((M_next * soil_vlm / S1 + Fd + F_Ia) >= soil_vlm,
                                                            soil_vlm - M_next * soil_vlm / S1,
                                                            Fd + F_Ia))  # in actual water, mm
            qm = np.where(zero_arr != 0, np.NAN, np.where((M_next * soil_vlm / S1 + Fd + F_Ia) >= soil_vlm,
                                                          q + Fd + F_Ia + M_next * soil_vlm / S1 - soil_vlm,
                                                          q))  # in actual water, mm
            qm = np.where(water == 1, 0, qm)
        else:
            PET_soil = PET

        # Calculate ET from soil profile
        ET_upper = np.where((S * soil_FC / S_abs / soil_FC_ave) > 1, 0,
                            PET_soil * (1 - (S * soil_FC / S_abs / soil_FC_ave) ** 2))
        ET_upper = np.where(zero_arr != 0, np.NAN,
                            np.where(ET_upper <= (M / S1 * soil_vlm), ET_upper, M / S1 * soil_vlm))
        ET_soil = PET_soil * (1 - (S * soil_FC / S1 / soil_FC_ave) ** 2)
        for x in RD_d.columns:
            if RD_d.loc[day, x] > 0:
                ET_soil = np.where((landuse_arr == int(x)) & (H_bal < RD_d.loc[day, x]) & (soil_z > RD_d.loc[day, x]),
                                   PET_soil * (1 - (S * soil_FC / (RD_d.loc[day, x] * S1 / soil_z) / soil_FC_ave) ** 2),
                                   np.where((landuse_arr == int(x)) & (H_bal < RD_d.loc[day, x]),
                                            PET_soil * (1 - (S * soil_FC / S1 / soil_FC_ave) ** 2), ET_soil))
        del x
        ET_soil = np.fmax(ET_upper, ET_soil)
        ET_lower = np.where(ET_soil - ET_upper <= (M_bal * (1 - M_dis) / S1 * soil_vlm), ET_soil - ET_upper,
                            M_bal * (1 - M_dis) / S1 * soil_vlm)
        # sum actual ET from canopy and from soil
        if prcp_d.loc[date] > 0:
            ET_act = ET_upper + ET_lower + ET_can
        else:
            ET_act = ET_upper + ET_lower

        # Record the parameters of the simulating day into file
        M_tot = np.nanmean(M_next / S1)
        ET_ave = np.nanmean(ET_act)
        parameters.write('%s\t%.3f\t%.2f\t%.2f\t%.2f\t%.2f\n' % (date, c_Ia_ave, ET_ave, Fc_ave, M_tot, TmpSoil))
        del c_Ia_ave
        del ET_ave
        del M_tot

        # Update moisture content in the unsaturated layer (M) by adding Fd_m and substracting ET_upper
        M_update_up = np.where(zero_arr != 0, np.NAN, np.where((M + (Fd_m - ET_upper) * S1 / soil_vlm) > 0,
                                                               M + (Fd_m - ET_upper) * S1 / soil_vlm,
                                                               0))  # in virtual water, mm
        # Adjust M_update_up value for water bodies
        M_update_up = np.where(water == 1, S_abs, M_update_up)
        M_rel = M_update_up / S_abs

        # Update water table depth in water bodies (res to res1)
        if prcp_d.loc[date] > 0:
            temp = np.where(water == 1, prcp - PET - Fc, np.NAN)
            res1 = res - np.nanmean(temp)
        else:
            temp = np.where(water == 1, PET, np.NAN)
            res1 = res + np.nanmean(temp)
        del temp

        # Account for irrigation
        if M_irrg > 0:
            if (day > irrg_start) & (day <= irrg_end):
                M_agrl = np.where(irrg == 1, M_rel, np.NAN)
                M_agrl_ave = np.nanmean(M_agrl)
                if M_agrl_ave < M_irrg:  # Irrigate agricultural field when average moisutre is below the threshold
                    print "The average relative moisture on irrigated fields is %.3f" % M_agrl_ave
                    M_update_irrg = np.where((irrg == 1) & (M_rel < soil_FC), soil_FC * S_abs,
                                             M_update_up)  # The moisture content after irrigation in the upper layer
                    irrg_water = (
                                         M_update_irrg - M_update_up) / S1 * soil_vlm  # The raster representing irrigated water, in actual water content, mm
                    res_irrg = np.nanmean(
                        irrg_water) / rate_water  # The value of irrigated water from water bodies, in mm\
                    del irrg_water
                    print "The amount of irrigated water from water bodies is %.1f mm" % res_irrg
                    res1 = res1 + res_irrg  # Update the water table depth in water bodies again by subtracting water for irrigation
                    M_update_up = M_update_irrg  # Update moisture content in the saturated layer again accounting for irrigation
                    M_rel = M_update_up / S_abs
                    del M_update_irrg
                    del M_agrl
                    del M_agrl_ave

        # Update M of the unsaturated layer again by representing percolation when the M_rel is above soil field capacity (soil_FC)
        del M_dis
        # Calculate updated M for different temperature days, in relative unit
        if TmpSoil >= 5:  # Under normal condition
            M_dis = np.where(M_rel > soil_FC, M_rel - (M_rel - soil_FC) * M_loss, M_rel)
        elif TmpSoil < 0:  # When average temperature is below 0 degrees Celsius, assume water moving velocity is reduced to 0.1 times of normal condition
            M_dis = np.where(M_rel > soil_FC, M_rel - (M_rel - soil_FC) * M_loss * 0.1, M_rel)
        else:  # When average temperature is between 0 and 5 degrees Celsius, assume water moving velocity is linearly changed with soil temperature
            M_dis = np.where(M_rel > soil_FC, M_rel - (M_rel - soil_FC) * M_loss * (0.18 * TmpSoil + 0.1), M_rel)
        M_dis = np.where((WI_rel <= 0) & (M_rel > soil_FC), M_rel,
                         np.where(WI_rel <= 0, soil_FC, M_dis))  # Adjust M_dis in wet areas where WI > WI_subs
        M_dis = np.where(water == 1, 1, M_dis)  # Adjust M_dis value for water bodies

        # Read out the relative M value of the unsaturated layers and the water table depth (H_bal) at the monitoring gauges
        # Sample M_dis
        for (key, value) in moisture_dic.items():
            MArr.loc[date, key] = M_dis[value[0][0], value[0][1]]
        del key
        del value
        # Sample H_bal
        for (key, value) in moisture_dic.items():
            HArr.loc[date, key] = H_bal[value[0][0], value[0][1]]
        del key
        del value

        # Calculate the mositure content of the whole soil profile after local water balance update, for the solution of water table accounting for global water balance below
        M_update = M_bal + M_update_up - ET_lower * S1 / soil_vlm  # in virtual water, mm

        # Clean up temporary numpy arrays, to release memory
        del M_rel
        del M_update_up
        del ET_act
        del ET_lower
        del ET_soil
        del ET_upper
        del PET_soil
        del PET
        del Fd_m
        del S
        del M
        del S_abs
        del M_next
        del M_bal
        del H_bal
        if prcp_d.loc[date] > 0:
            del F_Ia
            del ET_can
            del Fc
            del Ia
            del Fd
            del q
            del Fc0
            del c_Ia

        """ Solve water table depth in water bodies (res) by iteration based on global water balance"""
        # Update water depth in water bodies temporarily (res_temp)
        res_temp = res1
        # Calculate the temporary M_bal according to the water depth in water bodies (res_temp)
        H_bal = np.where(zero_arr != 0, np.NAN,
                         np.where(WI_rel >= 0, res_temp / 1000 + WI_rel / soil_f0, res_temp / 1000))
        H_bal = np.fmin(soil_z, H_bal)
        M_bal = (1 - H_bal / soil_z) * S1
        # Calculate the temporary total moisture accordingly
        M_next = np.where(M_bal < S1, M_bal + M_dis * (S1 - M_bal), M_bal)
        M_next = np.where(water == 1, S1, M_next)  # Adjust M_next for water bodies
        # Calculate the water table depth based on water balance (res_should)
        temp = (M_next - M_update) / S1 * soil_vlm  # in actual water
        res_should = res1 + np.nanmean(temp) / rate_water
        del temp

        # Use a while loop to prioritize res variation, making the difference between res_should and res_temp smaller than 10 mm
        n = 1
        # Initiate res_error, res_mx, res_mn
        res_error = res_should - res_temp
        if res_error < 0:
            res_mx = res_temp
            res_mn = res_should
        else:
            res_mx = res_should
            res_mn = res_temp
        while (res_error > 10) | (res_error < - 10):
            if res_error > 10:
                res_mx = min(res_should, res_mx)
                res_mn = max(res_temp, res_mn)
            elif res_error < -10:
                res_mx = min(res_temp, res_mx)
                res_mn = max(res_should, res_mn)
            res_temp = (res_mx + res_mn) / 2
            H_bal = np.where(zero_arr != 0, np.NAN,
                             np.where(WI_rel >= 0, res_temp / 1000 + WI_rel / soil_f0, res_temp / 1000))
            H_bal = np.fmin(soil_z, H_bal)
            M_bal = (1 - H_bal / soil_z) * S1
            M_next = np.where(M_bal < S1, M_bal + M_dis * (S1 - M_bal), M_bal)
            M_next = np.where(water == 1, S1, M_next)
            temp = (M_next - M_update) / S1 * soil_vlm
            res_should = res1 + np.nanmean(temp) / rate_water
            del temp
            res_error = res_should - res_temp
            n += 1
            if n > 20:
                if abs(res_error) > 10:
                    print "res is not prioritized within 10 mm error, res_error = %.2f mm" % res_error
                break
        del n

        # Treat the extra water due to a negative value of solved res as saturation excess runoff or subsurface return flow
        # Limit H_bal, M_bal, M_next0, Calculate the M_bal when res equals to 0 (use 1mm instead of 0 to avoid 0 as divider)
        if res_temp <= 0:
            H_bal0 = np.fmax(H_bal, H_temp)
            M_bal0 = (1 - H_bal0 / soil_z) * S1
            M_next0 = M_bal0 + M_dis * (S1 - M_bal0)
            M_next0 = np.where(water == 1, S1, M_next0)
        # On rain day, the extra water is simulated as saturation excess runoff
        if prcp_d.loc[date] > 1:
            if res_temp <= 0:
                qm = np.where(water == 1, max(-res_should, 0), qm + (
                        M_next - M_next0) / S1 * soil_vlm)  # qm is the raster representing total surface runoff
                temp_rf = np.where(zero_arr != 0, np.NAN, np.where(qm > prcp, qm - prcp,
                                                                   0))  # Limit qm smaller than prcp of the day, the extra was simulated as subsurface return flow
                qm = np.where(zero_arr != 0, np.NAN,
                              np.where(qm > prcp, prcp, qm))  # Limit qm smaller than prcp of the day
            elif res_should < 0:
                qm = np.where(water == 1, -res_should, qm)
                temp_rf = np.where(zero_arr != 0, np.NAN, np.where(qm > prcp, qm - prcp, 0))
                qm = np.where(zero_arr != 0, np.NAN, np.where(qm > prcp, prcp, qm))
            qm_ds = gdal.GetDriverByName("GTiff").CreateCopy(outputGdb + '/q%s.tif' % date, zero_ds, strict=0)
            qm_ds.GetRasterBand(1).WriteArray(qm)
        else:  # On no-rain day, the extra water is simulated as subsurface return flow
            if res_temp <= 0:
                temp_rf = np.where(water == 1, max(-res_should, 0), (M_next - M_next0) / S1 * soil_vlm)
            elif res_should < 0:
                temp_rf = np.where(zero_arr != 0, np.NAN, np.where(water == 1, -res_should, 0))
        try:
            for (key, value) in subwtshd_dic.items():
                current_array = np.where(value == 1, temp_rf, np.NAN)
                rOpArr.loc[date, key] = (np.nanmean(current_array)) * area_subs[key] / 1000 / 3600 / 24  # in cms
                del current_array
            del key
            del value
            del temp_rf
        except NameError:
            pass

        # Account for direct change of streamflow caused by fluctuations of stream water table
        bf_adj = (res - max(res_should, 0)) * 0.5 * rate_stream  # in mm
        if bf_adj < 0:
            bOp_adj = bf_adj * area_tot / 1000 / 3600 / 24  # in cms
            bOp_adj = max(bOp_adj, - bOpArr.xs(date, axis=0).max())  # Avoid negative bOp
            bf_adj = bOp_adj * 1000 * 3600 * 24 / area_tot  # in mm
            del bOp_adj
        for (key, value) in area_subs.items():
            bOpArr_adj.loc[date, key] = bf_adj * value / 1000 / 3600 / 24  # in cms
        del key
        del value

        # Limit H_bal, M_bal, M_next and res
        if res_temp <= 0:
            M_bal = np.copy(M_bal0)
            M_next = np.copy(M_next0)
            del M_next0
            del M_bal0
            del H_bal0
        # Update water table depth (res) for the next simulation day
        res = max(res_should, 0) + bf_adj / rate_water
        del res1

        # Update the M raster, the absolute S raster, for runoff calculation by CN method for the next day
        S_abs = S1 - M_bal
        M = M_dis * S_abs
        print "%s %.3f" % (date, res)
        del M_update

        # Calculate the travel time of surface flow
        if qm_ds != None:
            qm_ds = None
            # Prepare flow rate for travel time calculation
            qv = qm / 3600000 / tGen  # Calculate overland flow rate, in m/s
            qv_ds = gdal.GetDriverByName("GTiff").CreateCopy(tempFolder + "/qv.tif", zero_ds, strict=0)
            qv_ds.GetRasterBand(1).WriteArray(qv)
            qv_ds = None
            zero_absorption_ds = gdal.GetDriverByName("GTiff").CreateCopy(tempFolder + "/zero_absorption.tif", zero_ds,
                                                                          strict=0)
            zero_absorption_ds = None
            routing.route_flux(tempFolder + "/fdr_m.tif", fdr_uri, tempFolder + "/qv.tif",
                               tempFolder + "/zero_absorption.tif", tempFolder + "/loss.tif",
                               tempFolder + "/qv_acc.tif", 'flux_only')
            # os.remove(tempFolder+"/qv.tif")
            # os.remove(tempFolder+"/zero_absorption.tif")
            # os.remove(tempFolder+"/loss.tif")
            qv_acc_ds = gdal.Open(tempFolder + "/qv_acc.tif", gdal.GA_ReadOnly)
            qv_acc = qv_acc_ds.ReadAsArray()
            qv_acc_ds = None
            # os.remove(tempFolder+"/qv_acc.tif")
            qv1 = np.where(stream == 1, qv_acc,
                           qv)  # Calculate in-channel flow rate, and merge the two rate in one array
            ci4ri = np.where(zero_arr != 0, np.NAN, np.where(qv1 < 0.000000001, 0.000000001,
                                                             qv1))  # Convert 0 rate into the smallest value, preventing 0 as divisor
            # Calculate travel time of surface runoff across a grid cell, in seconds
            v = np.where(water == 1, v_lake, np.where(stream == 1,
                                                      np.power(slp_v, 0.3) * np.power(ci4ri * (cellSize ** 2), 0.4) / (
                                                              np.power(n_Mnng, 0.6) * np.power(strWidth, 0.4)),
                                                      np.power(slp_v, 0.3) * np.power(ci4ri, 0.4) * np.power(length,
                                                                                                             0.4) / np.power(
                                                          n_Mnng, 0.6)))
            t = length / v
            v_ds = gdal.GetDriverByName("GTiff").CreateCopy(tempFolder + "/v_reverse.tif", zero_ds, strict=0)
            v_ds.GetRasterBand(1).WriteArray(1 / v)
            v_ds = None
            t_ds = gdal.GetDriverByName("GTiff").CreateCopy(outputGdb + '/t%s.tif' % date, zero_ds, strict=0)
            t_ds.GetRasterBand(1).WriteArray(t)
            t_ds = None
            # Calculate the cumulative travel time, in hours
            routing.distance_to_stream(fdr_uri, outputGdb + "/outlet_ras.tif", outputGdb + '/tCon%s.tif' % date,
                                       tempFolder + "/v_reverse.tif")
            # os.remove(tempFolder+"/v_reverse.tif")
            flowTime_ds = gdal.Open(outputGdb + '/tCon%s.tif' % date, gdal.GA_Update)
            flowTime = flowTime_ds.ReadAsArray()
            flowTime_ndv = flowTime_ds.GetRasterBand(1).GetNoDataValue()
            tCon = np.where(flowTime != flowTime_ndv, flowTime / 3600, flowTime_ndv)
            flowTime_ds.GetRasterBand(1).WriteArray(tCon)
            flowTime_ds = None
            del flowTime
            del tCon
            del t
            del v
            del ci4ri
            del qv1
            del qv_acc
            del qv
            del qm
            del tGen

        # Complete the hydrologic simulation of one day, and continue the next day
        date_n += 1

    # Close output files for parameters
    parameters.close()
    del parameters

    # Write the base flow (bOpArr) out in a file
    bOpArr = bOpArr + bOpArr_adj
    bOpArr[bOpArr < 0] = 0
    bOpArr.to_csv(bFlow_File, header=True, index=True, index_label="date", float_format='%.4f', sep='\t', mode='a')
    del bOpArr_adj

    # Write the subsurface return flow (rOpArr) out in a file
    rOpArr.to_csv(rFlow_File, header=True, index=True, index_label="date", float_format='%.4f', sep='\t', mode='a')

    # Write the sampled relative moisture content in the unsaturated layer at the selected moisture sites in a file
    MArr.to_csv(M_File, header=True, index=True, index_label="date", float_format='%.4f', sep='\t', mode='a')
    del MArr

    # Write the sampled water table depth at the monitoring sites in a file
    HArr.to_csv(H_File, header=True, index=True, index_label="date", float_format='%.4f', sep='\t', mode='a')
    del HArr

    # os.remove(outputGdb+"/outlet_ras.tif")
    del length
    del landuse_arr
    del zero_arr
    del soil_z
    del soil_FC
    del soil_vlm
    del water
    del stream
    del irrg
    del strWidth
    del n_Mnng
    del Fc0_normal
    del Fc0_winter
    del S1
    del slp_v
    del WI_rel
    del M_loss
    del H_temp

    print 'Simulation finished, start routing.'

    """Calculate the surface flow that reaches the watershed outlet for a specific day"""
    # Create a pandas DataFrame to store surface flow that reach the discharge sites, in cms
    qOpArr = pd.DataFrame(np.zeros((len(dates), len(discharge_dic)), dtype=np.float32), dates,
                          columns=discharge_dic.keys())
    date_n = dates.get_loc(dayRouting)
    while date_n < len(dates):
        progressCheck = round(progressCheck + 50.0 / len(dates), 2)
        progressBar(progress, label, progressCheck)
        # Prepare a string representing the simulating date
        date = str(dates[date_n].year * 10000 + dates[date_n].month * 100 + dates[date_n].day)
        # Calculate and write out surface flow that reach the monitoring gauges each day
        qOutput.write(str(dates[date_n].year) + '-' + str(dates[date_n].month) + '-' + str(dates[date_n].day) + '\t')
        # Initiate a dictionary to temporarily store numpy arrays that represent cummulative surface runoff reaching the discharge sites, in mm
        qOp_dic = {}
        for (key, subwtshd) in subwtshd_dic.items():
            qOp_dic[key] = np.where(subwtshd == 1, 0.0, np.NAN)
        del key
        del subwtshd
        x = 1
        while x <= 7:
            date_x = str(dates[date_n - x + 1].year * 10000 + dates[date_n - x + 1].month * 100 + dates[
                date_n - x + 1].day)  # Prepare a string representing the date (x-1) days before the simulatiing day

            if os.path.isfile(outputGdb + '/q%s.tif' % date_x):
                q_ds = gdal.Open(outputGdb + '/q%s.tif' % date_x, gdal.GA_ReadOnly)
                if q_ds != None:
                    # Read surface flow raster q in numpy array
                    q_arr = q_ds.ReadAsArray()
                    q_ds = None
                    # Read cummulative travel time tCon in numpy array
                    tCon_ds = gdal.Open(outputGdb + '/tCon%s.tif' % date_x, gdal.GA_ReadOnly)
                    tCon_arr = tCon_ds.ReadAsArray()
                    tCon_ds = None
                    # Prepare Tsub_dic
                    Tsub_dic = {}
                    for (key,
                         value) in discharge_dic.items():  # Sample the tCon raster with given discharge sites (sitesDischarge)
                        Tsub_dic[key] = tCon_arr[value[0], value[1]]
                    del key
                    del value
                    for (key,
                         subwtshd) in subwtshd_dic.items():  # Prepare adjusted cummulative travel time raster by subtracting T_sub from the original tCon raster
                        T_sub = Tsub_dic[key]
                        tCon_mod = np.where(subwtshd == 1, tCon_arr - Tsub_dic[key], np.NAN)
                        qOp_dic[key] = np.where((tCon_mod <= 24 * x - 12) & (tCon_mod > 24 * x - 36),
                                                qOp_dic[key] + q_arr, qOp_dic[key])
                    del Tsub_dic
                    del key
                    del subwtshd
                    del q_arr
                    del tCon_arr
                    del tCon_mod
                else:
                    del q_ds
            x += 1
        for (key, qOp) in qOp_dic.items():
            qOp_ave = np.nanmean(qOp) * area_subs[key] / 1000 / 3600 / 24  # in cms
            qOpArr.loc[date, key] = qOp_ave  # Store result in the pandas dataframe
            qOutput.write('%.4f\t' % qOp_ave)  # Write result in the text file for surface flow output
            del qOp_ave
        del key
        del qOp
        del qOp_dic
        qOutput.seek(-1, 1)
        qOutput.truncate()
        qOutput.write('\n')

        # Calculate and write out total flow
        fOp = bOpArr.loc[date] + qOpArr.loc[date] + rOpArr.loc[date]
        fOutput.write(str(dates[date_n].year) + '-' + str(dates[date_n].month) + '-' + str(dates[date_n].day) + '\t')
        for key in discharge_dic.keys():
            fOutput.write('%.4f\t' % fOp[key])
        del key
        fOutput.seek(-1, 1)
        fOutput.truncate()
        fOutput.write('\n')
        del fOp

        # Continue the next day
        date_n += 1

        if date_n % 10 == 0:
            print 'Day %s finished.' % date

    # Close output files for surface flow and total flow
    del qOpArr
    qOutput.close()
    del qOutput
    fOutput.close()
    del fOutput
    zero_ds = None
    # os.remove(outputGdb+"/zero_raster.tif")

    # shutil.rmtree(tempFolder)

    print 'Voila! DHM-WM global water balance routine has completed your task.'
    print("--- %s seconds ---" % (time.time() - start_time))
    progressBar(progress, label, 100)


def Tiled_DHM_Function(frame, rowno, inputRasterFolder, inputVectorFolder, outputGdb, outputTxt, tempFolder,
                       outlet_name, fdr_uri, soil_uri, landuse_uri, dem_uri, watershed_uri, stream_uri,
                       sitesDischarge_uri, landuseFile, soilFile, prcp_File,
                       rainDis12_File, rainDis24_File, tmp_File, haveDailyPET, PET_method, haveDailyKc,
                       Kc_d_File, cIa_d_File, startDay, endDay, dayRouting, haveDisPrcp=None,
                       DisPrcpFolder=None, PET_File=None, wind_File=None, SSD_File=None,
                       humidity_File=None):
    # Set calibrated parameters
    progress = ttk.Progressbar(frame, orient=HORIZONTAL, length=150, mode='determinate')
    progress.grid(row=rowno + 1, column=1, sticky="W")
    label = Label(frame, bg="White")
    label.grid(row=rowno + 2, column=1, sticky="W")
    progressBar(progress, label, 10)
    CN_m = 0.90  # Set the modified factor for CN
    c_Ia_m = 0.90  # Set the modified factor for the initial c_Ia
    fc0 = 0.016  # Set constant gravitational infiltration rate, in range 0-1.000
    Kb = 15.0  # Set baseflow storage coefficient, in days
    tile = True  # Set whether tile flow module is active
    # Set the parameters related to tile drainage if tile flow module is active
    if tile == True:
        tLag = 48.0  # Set the lag coefficient for tile flow, in hours
        tDrain = 40.0  # Set the time to drain water in soils with Soil Hydrologic Group D, in hours
        CN_tile = 0.95
        tileDepth = 1000  # Set the depth of tiles to surface in mm
        tFlow_mx = 10.0  # Set the maximum tile flow in mm per square meters per day
        tileList = ['WWHT', 'CORN', 'SOYB', 'RNGE']
    # Initate some variables
    TmpSoil = -4.0  # Set the initial soil temperature in degrees Celsius
    # Set other parameters
    Latitude = 41.5  # Set the geographic latitude of the watershed in degrees
    soil_bd = 1.60  # Set the average moist bulk density of soil in Mg per cubic meters
    n_Mnng_streams = 0.025  # Set the Manning's n roughness coefficient for streams/channels
    v_lake = 0.0429  # Set the velocity of water flow in lakes/reservoirs/ponds in meter per second

    """ Set output text file names """
    parameter_Output = "parameters_test.txt"  # Set the output file name of parameters
    Qsur_Output = "qOutput_test.txt"  # Set the output file name of surface flow at the selected discharge sites
    Qgrd_Output = "bOutput_test.txt"  # Set the output file name of ground water flow at the selected discharge sites
    Qtot_Output = "fOutput_test.txt"  # Set the output file name of total streamflow at the selected discharge sites
    if tile == True:  # Set the output file name of tile flow at the selected discharge sites, if tile flow module is active
        Qtile_Output = "tOutput_test.txt"
    """
    -----------------------------------------------------------------------------------------------------------------
    Above is input of the model, including data and parameters, below is model analysis.
    Generally, there is no need to change the content below, unless modifying the model or do continuous simulation.
    -----------------------------------------------------------------------------------------------------------------
    """

    warnings.filterwarnings("ignore", category=RuntimeWarning)

    """ Define some functions """

    def make_constant_raster_from_base(base_dataset_uri, constant_value, out_uri, out_datatype=None, nodata_value=None):
        """ Create a raster with the same extent, projection with the base raster, but with constant value set by users """
        base_ds = gdal.Open(base_dataset_uri)
        gt_gdal = base_ds.GetGeoTransform()
        prj_gdal = base_ds.GetProjectionRef()
        if out_datatype == None:
            out_datatype = base_ds.GetRasterBand(1).DataType
        out_ds = gdal.GetDriverByName("GTiff").Create(out_uri, base_ds.RasterXSize, base_ds.RasterYSize,
                                                      base_ds.RasterCount, eType=out_datatype)
        out_ds.SetGeoTransform(gt_gdal)
        out_ds.SetProjection(prj_gdal)
        base_arr = base_ds.ReadAsArray()
        ndv = base_ds.GetRasterBand(1).GetNoDataValue()
        if nodata_value == None:
            nodata_value = ndv
        out_arr = np.where(base_arr != ndv, constant_value, nodata_value)
        out_ds.GetRasterBand(1).WriteArray(out_arr)
        out_ds.GetRasterBand(1).SetNoDataValue(nodata_value)
        base_ds = None
        out_ds = None

    def clip_GeoTiff_with_polygon(raster_input_uri, raster_output_uri, polygon_uri):
        """ Clip a GeoTiff raster within the mask of a polygon dataset """
        # Get the information of input raster and polygon
        raster_ds = gdal.Open(raster_input_uri, gdal.GA_ReadOnly)
        raster_arr = raster_ds.ReadAsArray()
        raster_geotransform = raster_ds.GetGeoTransform()
        ndv = raster_ds.GetRasterBand(1).GetNoDataValue()
        raster_datatype = raster_ds.GetRasterBand(1).DataType
        x_min_ras, y_max_ras = raster_geotransform[0], raster_geotransform[3]
        pixelSize = (abs(raster_geotransform[1]) + abs(raster_geotransform[5])) / 2
        vector_ds = ogr.Open(polygon_uri)
        vector_ly = vector_ds.GetLayer(0)
        source_srs = vector_ly.GetSpatialRef()
        x_min, x_max, y_min, y_max = vector_ly.GetExtent()
        x_res = int(round((x_max - x_min) / pixelSize))
        y_res = int(round((y_max - y_min) / pixelSize))
        # Create a output raster from the input polygon
        out_ras_ds = gdal.GetDriverByName("GTiff").Create(raster_output_uri, x_res, y_res, 1, raster_datatype)
        out_ras_ds.SetProjection(source_srs.ExportToWkt())
        out_ras_ds.SetGeoTransform([x_min, pixelSize, 0, y_max, 0, -pixelSize])
        out_ras_ds.GetRasterBand(1).SetNoDataValue(ndv)
        gdal.RasterizeLayer(out_ras_ds, [1], vector_ly, burn_values=[1])
        out_ras_arr = out_ras_ds.ReadAsArray()
        vector_ds = None
        # Calculate the indices for the clipped extent of raster array
        x_index = int(round((x_min - x_min_ras) / pixelSize))
        y_index = int(round((y_max_ras - y_max) / pixelSize))
        # Mask input raster with polygon, and export output raster
        raster_out_arr = np.where(out_ras_arr == 1, raster_arr[y_index:y_index + y_res, x_index:x_index + x_res], ndv)
        out_ras_ds.GetRasterBand(1).WriteArray(raster_out_arr)
        out_ras_ds = None

    def zonal_mean_with_raster(value_raster_input_uri, zones_raster_input_uri):
        """ Calculate zonal mean of value_raster_input_uri within each zones represented by the values of
            the zones_raster_input_uri, ignoring no_data values.
            return a dictionary, with keys representing zone values values representing zonal mean.
            Note: the value_raster_input and the zones_raster_input should be aligned (with the same extent and pixel size)."""
        value_ds = gdal.Open(value_raster_input_uri, gdal.GA_ReadOnly)
        value_arr = value_ds.ReadAsArray()
        ndv_value = value_ds.GetRasterBand(1).GetNoDataValue()
        value_arr = np.where(value_arr == ndv_value, np.NAN, value_arr)
        value_ds = None
        zones_ds = gdal.Open(zones_raster_input_uri, gdal.GA_ReadOnly)
        ndv_zones = zones_ds.GetRasterBand(1).GetNoDataValue()
        zones_arr = zones_ds.ReadAsArray()
        zones_ds = None
        zonal_mean = {}
        for x in range(1, max(map(max, zones_arr)) + 1, 1):  # np.unique(zones_arr):
            if x != ndv_zones:
                current_array = np.where(zones_arr == x, value_arr, np.NAN)
                mean_value = np.nanmean(current_array)
                zonal_mean[x] = mean_value
            else:
                zonal_mean[x] = ndv_value
        return zonal_mean

    # for x in np.unique(zones_arr):
    #         if x != ndv_zones:
    #                 current_array = np.where(zones_arr == x, value_arr, np.NAN)
    #                 mean_value = np.nanmean(current_array)
    #                 zonal_mean[x] = mean_value
    # return zonal_mean

    def evapotranspiration_FAO_PM(T_max, T_min, altitude, u10, RH_ave, day_of_year, latitude, SSD, albedo=0.23):
        # Calculate parameters from temperature and altitude
        T_mean = (T_max + T_min) / 2
        P = 101.3 * (((293 - 0.0065 * altitude) / 293) ** 5.26)
        pschm_constant = 0.665 * 0.001 * P
        vpc_slope = 4098 * 0.6108 * math.exp(17.27 * T_mean / (T_mean + 237.3)) / ((T_mean + 237.3) ** 2)
        # Calculate vapor pressure deficit:
        e0_max = 0.6108 * math.exp(17.27 * T_max / (T_max + 237.3))
        e0_min = 0.6108 * math.exp(17.27 * T_min / (T_min + 237.3))
        e_sat = (e0_max + e0_min) / 2
        e_act = e_sat * RH_ave / 100.0
        e_deficit = e_sat - e_act
        # Calculate Radiation
        dr = 1 + 0.033 * math.cos(2 * math.pi / 365 * day_of_year)
        sd = 0.409 * math.sin(2 * math.pi / 365 * day_of_year - 1.39)
        ws = math.acos(-math.tan(Latitude * math.pi / 180) * math.tan(sd))
        Ra = 24 * 60 / math.pi * 0.0820 * dr * (ws * math.sin(latitude * math.pi / 180) * math.sin(sd) +
                                                math.cos(latitude * math.pi / 180) * math.cos(sd) * math.sin(ws))
        N = 24 / math.pi * ws
        Rs = (0.25 + 0.50 * SSD / N) * Ra
        Rs0 = (0.75 + 0.00002 * altitude) * Ra
        Rns = (1 - albedo) * Rs
        Rs_rate = min(Rs / Rs0, 1.0)
        Rnl = 4.903 * 1e-09 * ((T_max + 273.16) ** 4 + (T_min + 273.16) ** 4) / 2 * (0.34 - 0.14 * (e_act ** 0.5)) * (
                1.35 * Rs_rate - 0.35)
        Rn = Rns - Rnl
        # Convert wind speed from 10m to 2m height
        u2 = u10 * 4.87 / math.log(67.8 * 10.0 - 5.42)
        # Calculate reference evapotranspiration from FAO Penman-Monteith equation
        PET = (0.408 * vpc_slope * Rn + pschm_constant * 900 / (T_mean + 273) * u2 * e_deficit) / (
                vpc_slope + pschm_constant * (1 + 0.34 * u2))
        return PET

    def evapotranspiration_Hargreaves(T_max, T_min, latitude, day_of_year):
        T_mean = (T_max + T_min) / 2
        dr = 1 + 0.033 * math.cos(2 * math.pi / 365 * day_of_year)
        sd = 0.409 * math.sin(2 * math.pi / 365 * day_of_year - 1.39)
        ws = math.acos(-math.tan(latitude * math.pi / 180) * math.tan(sd))
        Ra = 24 * 60 / math.pi * 0.0820 * dr * (ws * math.sin(latitude * math.pi / 180) * math.sin(sd) +
                                                math.cos(latitude * math.pi / 180) * math.cos(sd) * math.sin(ws))
        PET = 0.0023 * (T_mean + 17.8) * ((T_max - T_min) ** 0.5) * Ra / (2.5 - 0.00237 * T_mean)
        return PET

    """Import rasters into numpy array"""
    fdr_ds = gdal.Open(fdr_uri, gdal.GA_Update)
    fdr_arr = fdr_ds.ReadAsArray()
    ndv_fdr = fdr_ds.GetRasterBand(1).GetNoDataValue()
    # clip the soil and landuse raster data with the delineated watershed from last step "watershed delineation"
    clip_GeoTiff_with_polygon(soil_uri, tempFolder + "/soil.tif", watershed_uri)
    soil_ds = gdal.Open(tempFolder + "/soil.tif", gdal.GA_ReadOnly)
    soil_arr = soil_ds.ReadAsArray()
    soil_ds = None
    clip_GeoTiff_with_polygon(landuse_uri, tempFolder + "/landuse.tif", watershed_uri)
    landuse_ds = gdal.Open(tempFolder + "/landuse.tif", gdal.GA_ReadOnly)
    landuse_arr = landuse_ds.ReadAsArray()
    landuse_ds = None
    if (fdr_arr.shape == landuse_arr.shape == soil_arr.shape) == False:
        print "Warning: the size of input rasters do not match."
    # Aligne fdr, soil, landuse data, in case the fdr data covers more areas
    fdr_arr = np.where(landuse_arr > 0, fdr_arr, ndv_fdr)
    fdr_arr = np.where(soil_arr > 0, fdr_arr, ndv_fdr)
    fdr_ds.GetRasterBand(1).WriteArray(fdr_arr)
    fdr_ds = None
    del fdr_arr

    """ Prepare a zero_raster as a temp to create new rasters """
    make_constant_raster_from_base(fdr_uri, 0.0, outputGdb + "/zero_raster.tif", nodata_value=np.NAN)
    zero_ds = gdal.Open(outputGdb + "/zero_raster.tif", gdal.GA_ReadOnly)
    zero_arr = zero_ds.ReadAsArray()

    # Calculate average altitude of the study area
    clip_GeoTiff_with_polygon(dem_uri, tempFolder + "/dem.tif", watershed_uri)
    dem_ds = gdal.Open(tempFolder + "/dem.tif", gdal.GA_ReadOnly)
    dem_arr = dem_ds.ReadAsArray()
    dem_ds = None
    dem_arr = np.where(zero_arr != 0, np.NAN, dem_arr)
    altitude = np.nanmean(dem_arr)
    del dem_arr
    # os.remove(tempFolder+"/dem.tif")

    """Import landcover and soil data, prepare Manning's n raster, CN raster, Soil_HG raster, soil_z, soil_k, soil_Pe, soil_Pt rasters"""
    soilData = np.genfromtxt(soilFile, skip_header=1,
                             dtype=[('Value', 'i4'), ('HSG', 'i4'), ('soil_z', 'f4'), ('soil_k', 'f4'), ('Pe', 'f4'),
                                    ('Pt', 'f4')])
    soilData.sort(0)
    landuseData = np.genfromtxt(landuseFile, skip_header=1, dtype=[('Value', 'i4'), ('Name', 'a4'), ('Manning_n', 'f4'),
                                                                   ('CN_A', 'f4'), ('CN_B', 'f4'), ('CN_C', 'f4'),
                                                                   ('CN_D', 'f4')])
    landuseData.sort(0)
    # Create soil hydrologic group raster (soilHG)
    soilHG = np.copy(zero_arr)
    for line in soilData:
        soilHG = np.where(soil_arr == int(line['Value']), float(line['HSG']), soilHG)
    del line
    soilHG_ds = gdal.GetDriverByName("GTiff").CreateCopy(outputGdb + "/soil_HG.tif", zero_ds, strict=0)
    soilHG_ds.GetRasterBand(1).WriteArray(soilHG)
    soilHG_ds = None
    # Create soil depth to impervious/restrictive layer raster (soil_z)
    soil_z = np.copy(zero_arr)
    for line in soilData:
        soil_z = np.where(soil_arr == int(line['Value']), float(line['soil_z']), soil_z)
    del line
    soil_z_ds = gdal.GetDriverByName("GTiff").CreateCopy(outputGdb + "/soil_z.tif", zero_ds, strict=0)
    soil_z_ds.GetRasterBand(1).WriteArray(soil_z)
    soil_z_ds = None
    # Create soil hydraulic conductivity raster (soil_k)
    soil_k = np.copy(zero_arr)
    for line in soilData:
        soil_k = np.where(soil_arr == int(line['Value']), float(line['soil_k']), soil_k)
    del line
    soil_k_ds = gdal.GetDriverByName("GTiff").CreateCopy(outputGdb + "/soil_k.tif", zero_ds, strict=0)
    soil_k_ds.GetRasterBand(1).WriteArray(soil_k)
    soil_k_ds = None
    # Create soil effective porosity raster (soil_Pe)
    soil_Pe = np.copy(zero_arr)
    for line in soilData:
        soil_Pe = np.where(soil_arr == int(line['Value']), float(line['Pe']), soil_Pe)
    del line
    soil_Pe_ds = gdal.GetDriverByName("GTiff").CreateCopy(outputGdb + "/soil_Pe.tif", zero_ds, strict=0)
    soil_Pe_ds.GetRasterBand(1).WriteArray(soil_Pe)
    soil_Pe_ds = None
    # Create soil total porosity raster (soil_Pt)
    soil_Pt = np.copy(zero_arr)
    for line in soilData:
        soil_Pt = np.where(soil_arr == int(line['Value']), float(line['Pt']), soil_Pt)
    del line
    soil_Pt_ds = gdal.GetDriverByName("GTiff").CreateCopy(outputGdb + "/soil_Pt.tif", zero_ds, strict=0)
    soil_Pt_ds.GetRasterBand(1).WriteArray(soil_Pt)
    soil_Pt_ds = None
    # Calculate Field Capacity (FC = Pt - Pe)
    soil_FC = (soil_Pt - soil_Pe) / soil_Pt  # in relative volumetric water content
    soil_FC_ave = np.nanmean(soil_FC)
    # Calculate the distributed soil capacity of water, in mm.
    soil_vlm = soil_Pt * soil_z * 1000
    del soil_Pt
    # Create CN2 raster, and a dictrionary to pair landuse values and landuse names
    CN2 = np.copy(zero_arr)
    landuseDic = {}
    for line in landuseData:
        CN2 = np.where((landuse_arr == int(line['Value'])) & (soilHG == 1), float(line['CN_A']), CN2)
        CN2 = np.where((landuse_arr == int(line['Value'])) & (soilHG == 2), float(line['CN_B']), CN2)
        CN2 = np.where((landuse_arr == int(line['Value'])) & (soilHG == 3), float(line['CN_C']), CN2)
        CN2 = np.where((landuse_arr == int(line['Value'])) & (soilHG == 4), float(line['CN_D']), CN2)
        landuseDic[line['Name']] = int(line['Value'])
    del line
    CN2 = CN2 * CN_m
    # Prepare numpy arrays with water, residential areas, and tile-drained fields representing as 1 and 0 elsewhere
    water = np.where(zero_arr != 0, np.NAN, np.where(landuse_arr == landuseDic['WATR'], 1, 0))
    if tile == True:
        landuseTile = np.copy(zero_arr)
        for item in tileList:
            landuseTile = np.where(landuse_arr == landuseDic[item], 1, landuseTile)
        del item
    if tile == True:
        CN2 = np.where(zero_arr != 0, np.NAN, np.where((soilHG >= 3) & (landuseTile == 1), CN_tile * CN2, CN2))
    CN2_ds = gdal.GetDriverByName("GTiff").CreateCopy(outputGdb + "/CN2.tif", zero_ds, strict=0)
    CN2_ds.GetRasterBand(1).WriteArray(CN2)
    CN2_ds = None
    # Prepare cellSize in meters
    cellSize = (abs(zero_ds.GetGeoTransform()[1]) + abs(zero_ds.GetGeoTransform()[5])) / 2
    # Prepare stream width raster as strWidth, in meter
    str_ds = ogr.Open(stream_uri)
    str_ly = str_ds.GetLayer(0)
    stream_ds = gdal.GetDriverByName("GTiff").CreateCopy(tempFolder + "/strWidth.tif", zero_ds, strict=0)
    # changed this because it wasn't working as the strWidth.tiff was empty and stream_rate=0 and WI_stream was also not working,
    # gdal.RasterizeLayer(stream_ds,[1],str_ly,options=["ATTRIBUTE=strWidth"])
    gdal.RasterizeLayer(stream_ds, [1], str_ly, burn_values=[1])
    strWidth = stream_ds.ReadAsArray()
    stream_ds = None
    # Prepare a numpy array with stream representing as 1 and 0 elsewhere
    stream = np.where(zero_arr != 0, np.NAN, np.where(strWidth != 0, 1, strWidth))
    # Create Manning's n numpy array
    n_Mnng = np.copy(zero_arr)
    for line in landuseData:
        n_Mnng = np.where(landuse_arr == int(line['Value']), float(line['Manning_n']), n_Mnng)
    del line
    n_Mnng = np.where(stream == 1, n_Mnng_streams, n_Mnng)

    del soilData
    del landuseData
    del soil_arr

    """Import climate data"""
    # Get daily rainfall data from prcp_d.txt file
    prcp_d = pd.read_csv(prcp_File, sep='\t', header=0, index_col=0, squeeze=True, parse_dates=True)
    # Get rainfall distribution data from 12raindis.txt and 24raindis.txt
    rainDis12 = pd.read_csv(rainDis12_File, sep='\t', header=0, index_col=0, squeeze=True)
    rainDis24 = pd.read_csv(rainDis24_File, sep='\t', header=0, index_col=0, squeeze=True)
    # Get daily temperature data from tmp_d.txt file
    tmp_d = pd.read_csv(tmp_File, sep='\t', header=0, index_col=0, parse_dates=True,
                        usecols=['date', 'TEM_max', 'TEM_min'], na_values=-99.9)
    tmp_d.fillna(tmp_d.rolling(7, min_periods=1, center=True).mean(), inplace=True)  # Fill with 7-day average values
    tmp_d.ffill(inplace=True)  # fill forward
    tmp_d.bfill(inplace=True)  # fill backward
    tmp_d['TEM_mean'] = (tmp_d.TEM_max + tmp_d.TEM_min) / 2
    TmpAirAn = tmp_d.TEM_mean.resample('A').mean()[tmp_d.TEM_mean.resample('A').count() > 350].mean()
    # if daily PET data is available, get daily PET data from PET_d.txt file
    if haveDailyPET == True:
        PET_d = pd.read_csv(PET_File, sep='\t', header=0, index_col=0, squeeze=True, parse_dates=True, na_values=-6999)
    # If PET method is FAO Penman-Monteith, get daily climate data needed (wind, sunshine duration, relative humidity)
    elif PET_method == 2:
        win_df = pd.read_csv(wind_File, sep='\t', header=0, index_col=0, parse_dates=True,
                             usecols=['date', 'WIN_ave'], na_values=-99.9)
        win_df.fillna(win_df.rolling(7, min_periods=1, center=True).mean(),
                      inplace=True)  # Fill with 7-day average values
        win_df.ffill(inplace=True)
        win_df.bfill(inplace=True)
        rh_df = pd.read_csv(humidity_File, sep='\t', header=0, index_col=0, parse_dates=True,
                            usecols=['date', 'RHU_ave'], na_values=-99)
        rh_df.fillna(rh_df.rolling(7, min_periods=1, center=True).mean(),
                     inplace=True)  # Fill with 7-day average values
        rh_df.ffill(inplace=True)
        rh_df.bfill(inplace=True)
        ssd_df = pd.read_csv(SSD_File, sep='\t', header=0, index_col=0, parse_dates=True,
                             usecols=['date', 'SSD'], na_values=-99.9)
        ssd_df.fillna(ssd_df.rolling(7, min_periods=1, center=True).mean(),
                      inplace=True)  # Fill with 7-day average values
        ssd_df.ffill(inplace=True)
        ssd_df.bfill(inplace=True)
    # if daily Kc data is available, get daily Kc data from Kc_d.txt file
    if haveDailyKc == True:
        Kc_d = pd.read_csv(Kc_d_File, sep='\t', header=0, index_col=0)
    # Get daily c_Ia parameter value from cIa_d.txt file
    cIa_d = pd.read_csv(cIa_d_File, sep='\t', header=0, index_col=0, squeeze=True)

    """Prepare some common variables"""
    # Prepare pandas dates for the simulation period
    dates = pd.date_range(startDay, endDay, None, 'D')
    # Calculate maximum damping depth of soil, in mm
    dd_mx = 1000 + 2500 * soil_bd / (soil_bd + 686 * math.exp(-5.63 * soil_bd))
    # Read X and Y coordinates of discharge sites in a dictionary,
    # and create a dictionary (outlets_dic) to store each discharge site in a seperate vector file.
    discharge_ds = ogr.Open(sitesDischarge_uri, False)
    discharge_ly = discharge_ds.GetLayer(0)
    srs = discharge_ly.GetSpatialRef()
    discharge_ly.ResetReading()
    discharge_defn = discharge_ly.GetLayerDefn()
    discharge_fieldlist = []
    for i in range(discharge_defn.GetFieldCount()):
        discharge_fieldlist += [discharge_defn.GetFieldDefn(i).GetName()]
    discharge_dic = {}
    outlets_dic = {}
    for feature in discharge_ly:
        if feature is not None:
            feature_name = feature.GetField(discharge_fieldlist.index('Name'))
            geom = feature.GetGeometryRef()
            feature_XY = [geom.GetX(), geom.GetY()]
            discharge_dic[feature_name] = feature_XY
            if os.path.exists(tempFolder + "/outlet" + str(feature_name) + ".shp"):
                ogr.GetDriverByName('ESRI Shapefile').DeleteDataSource(
                    tempFolder + "/outlet" + str(feature_name) + ".shp")
            outletds = ogr.GetDriverByName('ESRI Shapefile').CreateDataSource(
                tempFolder + "/outlet" + str(feature_name) + ".shp")
            tempShapeEncode = (tempFolder + "/outlet" + str(feature_name) + ".shp").encode('utf-8')
            outletly = outletds.CreateLayer(tempShapeEncode, srs=srs, geom_type=ogr.wkbPoint)
            outletDefn = outletly.GetLayerDefn()
            outFeature = ogr.Feature(outletDefn)
            outFeature.SetGeometry(geom)
            outletly.CreateFeature(outFeature)
            outFeature.Destroy()
            outletds = None
            outlets_dic[feature_name] = tempFolder + "/outlet" + str(feature_name) + ".shp"
    discharge_ds = None
    del srs
    del discharge_fieldlist
    del feature
    del feature_name
    del geom
    del feature_XY
    del outFeature
    del outletly
    del outletds
    del outletDefn
    # Convert X and Y coordinates of discharge sites into row and column indices of rasters
    originX = zero_ds.GetGeoTransform()[0]
    originY = zero_ds.GetGeoTransform()[3]
    pixelWidth = zero_ds.GetGeoTransform()[1]
    pixelHeight = zero_ds.GetGeoTransform()[5]
    for (key, value) in discharge_dic.items():
        X_index = int(math.floor((value[0] - originX) / pixelWidth))
        Y_index = int(math.floor((value[1] - originY) / pixelHeight))
        discharge_dic[key] = [Y_index, X_index]
    del key
    del value
    del X_index
    del Y_index
    # Prepare outlet_ras raster (rasterized outlet site data) for distance_to_stream analysis
    make_constant_raster_from_base(fdr_uri, 0, outputGdb + "/outlet_ras.tif", out_datatype=gdal.GDT_Byte,
                                   nodata_value=255)
    outlet_ras_ds = gdal.Open(outputGdb + "/outlet_ras.tif", gdal.GA_Update)
    outlet_ras = outlet_ras_ds.ReadAsArray()
    outlet_ras[discharge_dic[outlet_name][0], discharge_dic[outlet_name][1]] = 1
    # Changed there's no need to do this it actually disrupts the 1 value
    # outlet_ras = np.where(zero_arr != 0, 255, outlet_ras)
    outlet_ras_ds.GetRasterBand(1).WriteArray(outlet_ras)
    outlet_ras_ds = None
    del outlet_ras
    # Generate a list of subwatershed raster arrays with given monitoring gauges
    subwtshd_dic = {}
    routing.routing_core.calculate_flow_weights(fdr_uri, tempFolder + "/outflow_weights.tif",
                                                tempFolder + "/outflow_dir.tif")
    for (key, value) in outlets_dic.items():
        routing.routing_core.delineate_watershed(tempFolder + "/outflow_dir.tif", tempFolder + "/outflow_weights.tif",
                                                 value, 0,
                                                 inputRasterFolder + "/stream_DL.tif",
                                                 tempFolder + "/watershed_" + str(key) + ".shp",
                                                 tempFolder + "/Moutlet" + key + ".shp")
        wtshd_ds = ogr.Open(tempFolder + "/watershed_" + str(key) + ".shp", False)
        wtshd_ly = wtshd_ds.GetLayer(0)
        make_constant_raster_from_base(fdr_uri, 0, tempFolder + "/wtshd_" + str(key) + ".tif",
                                       out_datatype=gdal.GDT_Byte, nodata_value=255)
        wtshd_raster_ds = gdal.Open(tempFolder + "/wtshd_" + str(key) + ".tif", gdal.GA_Update)
        gdal.RasterizeLayer(wtshd_raster_ds, [1], wtshd_ly, burn_values=[1])
        wtshd_arr = wtshd_raster_ds.ReadAsArray()
        wtshd_raster_ds = None
        wtshd_ds = None
        subwtshd_dic[key] = wtshd_arr
    # os.remove(tempFolder+"/wtshd_"+str(key)+".tif")
    # ogr.GetDriverByName("ESRI Shapefile").DeleteDataSource(tempFolder+"/Moutlet"+str(key)+".shp")
    del key
    del value
    del outlets_dic
    # Generate a list of the areas for each subwatersheds with monitoring gauges, in square meters
    temp_arr = np.where(zero_arr == 0, 1, 0)
    area_tot = (np.count_nonzero(temp_arr)) * (cellSize ** 2)
    del temp_arr
    area_subs = {}
    for (key, value) in subwtshd_dic.items():
        temp = np.where(value == 1, 1, 0)
        area_subs[key] = np.count_nonzero(temp) * (cellSize ** 2)
        del temp
    del key
    del value
    # Change the flow direction at the outlet to no_data value for flow_accumulation analysis
    fdr_ds = gdal.Open(fdr_uri, gdal.GA_ReadOnly)
    fdr_m_ds = gdal.GetDriverByName("GTiff").CreateCopy(tempFolder + "/fdr_m.tif", fdr_ds, strict=0)
    fdr_m_arr = fdr_m_ds.ReadAsArray()
    fdr_m_arr[discharge_dic[outlet_name][0], discharge_dic[outlet_name][1]] = ndv_fdr
    fdr_m_ds.GetRasterBand(1).WriteArray(fdr_m_arr)
    fdr_m_ds = None
    del fdr_m_arr
    del ndv_fdr
    fdr_ds = None
    # Calculate ground flow routing parameters
    g0 = 1 / Kb / (2 + 1 / Kb)
    g1 = g0
    g2 = (2 - 1 / Kb) / (2 + 1 / Kb)

    """ Prepare the output files """
    # Writh the head of average c_Ia, ET, Fc, M and TmpSoil values of simulating days
    parameters = open(outputTxt + '/' + parameter_Output, 'a')
    parameters.write(
        'The average c_Ia, ET, Fc, M_relative and TmpSoil values are estimated by DHM-WM local water balance routine as below:\n')
    parameters.write('date\tc_Ia\tET(mm)\tFc(mm)\tM_rel\tTmpSoil(C)\n')
    # Write the head of output surface flow
    qOutput = open(outputTxt + '/' + Qsur_Output, 'a')
    qOutput.write(
        'The surface flow at the sub/watershed outlet(s) is simulated by DHM-WM local water balance routine as below:\n')
    qOutput.write('date\t')
    for key in discharge_dic.keys():
        qOutput.write(str(key) + '\t')
    qOutput.seek(-1, 1)
    qOutput.truncate()
    qOutput.write('\n')
    del key
    # Write the head of output total streamflow
    fOutput = open(outputTxt + '/' + Qtot_Output, 'a')
    fOutput.write(
        'The total streamflow at the sub/watershed outlet(s) is simulated by DHM-WM local water balance routine as below:\n')
    fOutput.write('date\t')
    for key in discharge_dic.keys():
        fOutput.write(str(key) + '\t')
    fOutput.seek(-1, 1)
    fOutput.truncate()
    fOutput.write('\n')
    del key
    # Set the output file name of base flow
    bFlow_File = outputTxt + '/' + Qgrd_Output
    bOutput = open(bFlow_File, 'w')
    bOutput.write(
        'The groundwater flow at the sub/watershed outlet(s) is simulated by DHM-WM local water balance routine as below:\n')
    bOutput.close()
    del bOutput
    # Set the output file name of tile flow, if tile module is active
    if tile == True:
        tFlow_File = outputTxt + '/' + Qtile_Output
        tOutput = open(tFlow_File, 'w')
        tOutput.write(
            'The tile flow at the sub/watershed outlet(s) is simulated by DHM-WM local water balance routine as below:\n')
        tOutput.close()
        del tOutput

    """Prepare some common rasters"""
    # Set the used Fc0
    Fc0_normal = fc0 * soil_k * 1000 / 24  # in mm/hr
    Fc0_winter = 0.1 * Fc0_normal  # Assume 0.1 times of gravitational infiltration during days when surface soil becomes frozen
    del soil_k
    # Prepare absolute retention parameter raster (S_abs_mx, here named S1)
    S2 = 25400 / CN2 - 254
    S1 = 2.281 * S2  # Set the absolute S (Sabs_mx)
    S1_ds = gdal.GetDriverByName("GTiff").CreateCopy(outputGdb + "/S_abs_mx.tif", zero_ds, strict=0)
    S1_ds.GetRasterBand(1).WriteArray(S1)
    S1_ds = None
    del S2
    del CN2
    # Prepare slope raster
    slp_ds = gdal.DEMProcessing(tempFolder + "/slp.tif", dem_uri, "slope", slopeFormat="percent")
    slp_ds = None
    clip_GeoTiff_with_polygon(tempFolder + "/slp.tif", tempFolder + "/slp1.tif", watershed_uri)
    slp_ds = gdal.Open(tempFolder + "/slp1.tif", gdal.GA_ReadOnly)
    slp_arr = slp_ds.ReadAsArray()
    slp_v = np.where(slp_arr < 0, np.NAN, np.where((slp_arr < 0.5) | (water == 1), 0.005, slp_arr / 100))
    slp_ds = None
    # del slp_arr
    # os.remove(tempFolder+"/slp.tif")
    # os.remove(tempFolder+"/slp1.tif")
    # Prepare grid cell flow length array for travel time calculation
    outflow_weight_ds = gdal.Open(tempFolder + "/outflow_weights.tif", gdal.GA_ReadOnly)
    outflow_weight = outflow_weight_ds.ReadAsArray()
    outflow_weight_ds = None
    outflow_dir_ds = gdal.Open(tempFolder + "/outflow_dir.tif", gdal.GA_ReadOnly)
    outflow_dir = outflow_dir_ds.ReadAsArray()
    outflow_dir_ds = None
    length1 = np.where(zero_arr != 0, np.NAN, np.where((outflow_dir % 2) == 1, 1.41421356237 * cellSize, cellSize))
    outflow_dir2 = np.where(zero_arr != 0, np.NAN, (outflow_dir + 1) % 8)
    length2 = np.where(zero_arr != 0, np.NAN, np.where((outflow_dir2 % 2) == 1, 1.41421356237 * cellSize, cellSize))
    length = length1 * outflow_weight + length2 * (1 - outflow_weight)
    del length1
    del length2
    del outflow_dir2
    del outflow_weight
    del outflow_dir
    # os.remove(tempFolder+"/outflow_weights.tif")
    # os.remove(tempFolder+"/outflow_dir.tif")
    length_ds = gdal.GetDriverByName("GTiff").CreateCopy(tempFolder + "/length.tif", zero_ds, strict=0)
    length_ds.GetRasterBand(1).WriteArray(length)
    length_ds = None
    # If tile flow module is active, prepare the rate of tile flow drainage raster for Soil Hydrologic Group C and D
    if tile == True:
        k_tDrain = np.where(zero_arr != 0, np.NAN, np.where(soilHG == 4, 1 - math.exp(-24 / tDrain),
                                                            np.where(soilHG == 3,
                                                                     min(1, 2 * (1 - math.exp(-24 / tDrain))), 0)))

    """Initiate some variables and rasters"""
    # Create a dictionary to store bOp values (in cms) for the current simulating day, and initiate it
    bOp = {}
    for (key, value) in area_subs.items():
        bOp[key] = 0.005 * value / 1000000
    del key
    del value
    # Initiate a dictionary to store Fc_ave (in mm) for each subwatersheds
    FcAve_dic = {}
    for key in area_subs.keys():
        FcAve_dic[key] = 0.0
    del key
    # Set the initial raster for moisture content in the unsaturated layer
    M_next = 0.5 * S1
    # Set the initial S values for the unsaturated layer
    S = S1 - M_next
    # If tile flow module is active, create a dictionary to store the initial tile flow (in mm) for each subwatersheds
    if tile == True:
        tFlow_next = {}
        for key in area_subs.keys():
            tFlow_next[key] = 0.0
    qm_ds = None

    """ Create some pandas DataFrame to store simulation results """
    # Create a pandas DataFrame to store bOp values
    bOpArr = pd.DataFrame(np.zeros((len(dates), len(discharge_dic)), dtype=np.float32), dates,
                          columns=discharge_dic.keys())
    # Create a pandas DataFrame to store tile flow values, if tile flow module is active
    if tile == True:
        tOpArr = pd.DataFrame(np.zeros((len(dates), len(discharge_dic)), dtype=np.float32), dates,
                              columns=discharge_dic.keys())

    """ DHM-WM local water balance routine starts simulation """
    date_n = 0
    progressBar(progress, label, 10)
    progressCheck = 10.0
    while date_n < len(dates):
        progressCheck = round(progressCheck + 40.0 / len(dates), 2)
        progressBar(progress, label, progressCheck)
    while date_n < len(dates):
        # Prepare a string of the simulateion date, and day of year
        date = str(dates[date_n].year * 10000 + dates[date_n].month * 100 + dates[date_n].day)
        day = dates[date_n].dayofyear

        # Calculate the baseflow routing
        for (key, value) in FcAve_dic.items():
            bOp[key] = (g0 + g1) * value * area_subs[key] / 1000 / 3600 / 24 + g2 * bOp[key]
            bOpArr.loc[date, key] = bOp[key]  # Store the baseflow results into pandas DataFrame
        del key
        del value

        # Update S values as S = S1 - M
        S = S1 - M_next
        M = S1 - S

        # Calculate the average soil temperature of the day in 500mm depth, as a representation of soil temperature
        # Calculate damping depth in mm
        dd_factor = np.nanmean(M_next) / ((0.356 - 0.144 * soil_bd) * (np.nanmean(S1)))
        dd = dd_mx * math.exp(math.log(500 / dd_mx) * (((1 - dd_factor) / (1 + dd_factor)) ** 2))
        del dd_factor
        # Calculate df
        zd = 500 / dd
        df = zd / (zd + math.exp(-0.867 - 2.078 * zd))
        del zd
        # Calculate soil temperature, assuming soil surface temperature is 1 degree lower than the average air temperature
        TmpSoil = 0.8 * TmpSoil + 0.2 * (
                df * (TmpAirAn - tmp_d.loc[date, 'TEM_mean'] - 1) + tmp_d.loc[date, 'TEM_mean'] - 1)
        del df

        # Use Mishra-Singh CN method to calculate surface runoff and relative variables
        if prcp_d.loc[date] > 0:
            # Prepare precipitation data first, use distributed data if available, or use the number in prcp_d.txt file
            if haveDisPrcp == True:
                prcp_ds = gdal.Open(DisPrcpFolder + 'prcp' + date + '.tif', gdal.GA_ReadOnly)
                prcp = prcp_ds.ReadAsArray()
                prcp_ds = None
            else:
                prcp = prcp_d.loc[date]
            # Prepare c_Ia
            c_Ia = c_Ia_m * cIa_d.loc[day] * S / S1
            c_Ia_ave = np.nanmean(c_Ia)
            # Estimate the duration of runoff using synthetic rainfall distribution curve
            tGen = np.where(zero_arr == 0, 0.5, np.NAN)
            if prcp_d.loc[
                date] < 50:  # Use 12-h synthetic rainfall distribution curve when daily precipitation is smaller than 50 mm
                for i in rainDis12.index[:-1]:
                    tGen = np.where((c_Ia * S < rainDis12.loc[i + 0.5] * prcp) & (c_Ia * S >= rainDis12[i] * prcp),
                                    12 - i, tGen)
                del i
            else:  # Use 24-h synthetic rainfall distribution curve when daily precipitation is larger than 50 mm
                for i in rainDis24.index[:-1]:
                    tGen = np.where((c_Ia * S < rainDis24[i + 0.5] * prcp) & (c_Ia * S >= rainDis24[i] * prcp), 24 - i,
                                    tGen)
                del i
            # Set actual Fc0 according to soil temperature and runoff generation time
            if TmpSoil < 0:
                Fc0 = Fc0_winter * tGen
            else:
                Fc0 = Fc0_normal * tGen
            # Calculate direct surface runoff with general Mishra-Singh model
            q = np.where(zero_arr != 0, np.NAN, np.where((c_Ia * S + Fc0) <= prcp,
                                                         (prcp - c_Ia * S - Fc0) * (prcp - c_Ia * S - Fc0 + M) / (
                                                                 prcp - c_Ia * S - Fc0 + M + S), 0))
            # Calculate gravitational infiltration Fc
            Fc = np.where(zero_arr != 0, np.NAN,
                          np.where((c_Ia * S + Fc0) <= prcp, Fc0, np.where((c_Ia * S) <= prcp, prcp - c_Ia * S, 0)))
            Fc_ave = np.nanmean(Fc)
            # Prepare FcAve_dic for base flow estimation on next simulation day
            for (key, value) in subwtshd_dic.items():
                current_array = np.where(value == 1, Fc, np.NAN)
                FcAve_dic[key] = np.nanmean(current_array)
                del current_array
            del key
            del value
            # Calculate dynamic infiltration Fd with soil moisture budgeting equation
            Fd = np.where(zero_arr != 0, np.NAN, np.where((c_Ia * S + Fc0) <= prcp, prcp - c_Ia * S - Fc - q, 0))
            # Calculate initial abstraction
            Ia = np.where(zero_arr != 0, np.NAN, np.where((c_Ia * S) <= prcp, c_Ia * S, prcp))
        else:
            c_Ia_ave = 0
            Fd_m = 0
            Fc_ave = 0
            for key in area_subs.keys():
                FcAve_dic[key] = 0.0
            del key

        # Calculate evapotranspiration ET
        # Determine the potential ET (PET)
        if haveDailyPET == False:  # if PET data is unavaiable, calculate PET using 1. Hargreaves method or 2. Panmen-Monteith method.
            if PET_method == 1:
                E = evapotranspiration_Hargreaves(tmp_d.loc[date, 'TEM_max'], tmp_d.loc[date, 'TEM_min'], Latitude, day)
            elif PET_method == 2:
                E = evapotranspiration_FAO_PM(tmp_d.loc[date, 'TEM_max'], tmp_d.loc[date, 'TEM_min'], altitude,
                                              win_df.loc[date, 'WIN_ave'],
                                              rh_df.loc[date, 'RHU_ave'], day, Latitude, ssd_df.loc[date, 'SSD'],
                                              albedo=0.23)
        elif date in PET_d.dropna().index:  # If PET data is available, use it directly
            E = PET_d[date]
        else:  # if the PET data in the simulation day is missing, calculate PET using Hargreaves method instead
            E = evapotranspiration_Hargreaves(tmp_d.loc[date, 'TEM_max'], tmp_d.loc[date, 'TEM_min'], Latitude, day)
        if E <= 0.0:
            E = 0.0
        if haveDailyKc == True:  # if daily Kc is available, adjust PET for different land cover and different day
            PET = E
            for x in Kc_d.columns:
                PET = np.where(landuse_arr == int(x), Kc_d.loc[day, x] * E, PET)
            del x
        else:
            PET = E

        # Incorporate c_Ia into water budget
        if prcp_d.loc[date] > 0:
            # Calculate ET from canopy interception (assume to be half of the Ia)
            F_Ia = np.where(zero_arr != 0, np.NAN, np.where(0.5 * Ia > PET, Ia - PET, 0.5 * Ia))
            ET_can = np.where(zero_arr != 0, np.NAN, np.where(0.5 * Ia > PET, PET, 0.5 * Ia))
            PET_soil = PET - ET_can  # Calculate PET from the soil profile
            # Adjust surface runoff (q to qm) and dynamic infiltration (Fd to Fd_m) accounting for actual water balance
            Fd_m = np.where(zero_arr != 0, np.NAN,
                            np.where((M * soil_vlm / S1 + Fd + F_Ia) >= soil_vlm, soil_vlm - M * soil_vlm / S1,
                                     Fd + F_Ia))  # in actual water, mm
            qm = np.where(zero_arr != 0, np.NAN, np.where((M * soil_vlm / S1 + Fd + F_Ia) >= soil_vlm,
                                                          q + Fd + F_Ia + M * soil_vlm / S1 - soil_vlm,
                                                          q))  # in actual water, mm
            if prcp_d.loc[date] > 1:
                qm_ds = gdal.GetDriverByName("GTiff").CreateCopy(outputGdb + '/q%s.tif' % date, zero_ds, strict=0)
                qm_ds.GetRasterBand(1).WriteArray(qm)
        else:
            PET_soil = PET

        # Calculate ET from soil profile
        ET_soil = np.where((S * soil_FC / S1 / soil_FC_ave) > 1, 0,
                           PET_soil * (1 - (S * soil_FC / S1 / soil_FC_ave) ** 2))
        ET_soil = np.where(zero_arr != 0, np.NAN, np.where(ET_soil <= (M / S1 * soil_vlm), ET_soil, M / S1 * soil_vlm))
        # sum actual ET from canopy and from soil
        if prcp_d.loc[date] > 0:
            ET_act = ET_soil + ET_can
        else:
            ET_act = ET_soil

        # Record the parameters of the simulating day into file
        M_rel = np.nanmean(M / S1)
        ET_ave = np.nanmean(ET_act)
        parameters.write('%s\t%.3f\t%.2f\t%.2f\t%.2f\t%.2f\n' % (date, c_Ia_ave, ET_ave, Fc_ave, M_rel, TmpSoil))
        del c_Ia_ave
        del ET_ave
        del M_rel

        # Calculate water flowing into tiles and update soil moisture content for the next day (M_next)
        if tile == True:
            # Calculate tile flow of the simulating day, only in agricultual fields where soil depth is deeper than the tile depth
            wtrDepth = np.where(zero_arr != 0, np.NAN, S / S1 * soil_z * 1000)
            if TmpSoil >= 5:
                tFlow = np.where(zero_arr != 0, np.NAN, np.where(
                    (landuseTile == 1) & (soilHG >= 3) & (soil_z * 1000 > tileDepth) & (tileDepth > wtrDepth),
                    (tileDepth - wtrDepth) * soil_Pe * k_tDrain, 0))
            elif TmpSoil < 0:
                # When average soil temperature is below 0 degrees celsius, assume k_tileDrain is 0.1 times of normal temperature
                tFlow = np.where(zero_arr != 0, np.NAN, np.where(
                    (landuseTile == 1) & (soilHG >= 3) & (soil_z * 1000 > tileDepth) & (tileDepth > wtrDepth),
                    (tileDepth - wtrDepth) * soil_Pe * 0.1 * k_tDrain, 0))
            else:
                # When average soil temperature is between 0 and 5 degrees celsius, assume the drainage velocity is linearly changed
                tFlow = np.where(zero_arr != 0, np.NAN, np.where(
                    (landuseTile == 1) & (soilHG >= 3) & (soil_z * 1000 > tileDepth) & (tileDepth > wtrDepth),
                    (tileDepth - wtrDepth) * soil_Pe * (0.18 * TmpSoil + 0.1) * k_tDrain, 0))
            tFlow = np.where(zero_arr != 0, np.NAN, np.where(tFlow <= tFlow_mx, tFlow,
                                                             tFlow_mx))  # Limit tile flow below the maximum drainage capacity
            # Calculate the M value for the next time step by adding modified infiltration Fd_m and subtracting tileFlow and ET_soil from M
            M_next = M + (Fd_m - ET_soil - tFlow) / soil_vlm * S1  # in virtual water
            M_next = np.where(zero_arr != 0, np.NAN, np.where(M_next < 0, 0, np.where(M_next > S1, S1, M_next)))
        else:
            # Calculate the M value for the next time step by adding Fd_m into soil moisture content and substracting ET_soil
            M_next = M + (Fd_m - ET_soil) / soil_vlm * S1  # in virtual water
            M_next = np.where(zero_arr != 0, np.NAN, np.where(M_next < 0, 0, np.where(M_next > S1, S1, M_next)))

        # Do flow routing for tile flow, and update tile flow pools for the next simulation day
        if tile == True:
            if TmpSoil >= 5:
                for (key, value) in subwtshd_dic.items():
                    current_array = np.where(value == 1, tFlow, np.NAN)
                    tFlow_ave = np.nanmean(current_array)
                    tOpArr.loc[date, key] = (tFlow_ave + tFlow_next[key]) * (1 - math.exp(-24 / tLag)) * area_subs[
                        key] / 1000 / 3600 / 24  # Calculate the tile flow reaching the discharge sites, in cms
                    tFlow_next[key] = (tFlow_ave + tFlow_next[key]) * math.exp(
                        -24 / tLag)  # Calculate the tile flow pool for the next simulation day, in mm
                    del current_array
                    del tFlow_ave
                del key
                del value
            elif TmpSoil < 0:
                for (key, value) in subwtshd_dic.items():
                    current_array = np.where(value == 1, tFlow, np.NAN)
                    tFlow_ave = np.nanmean(current_array)
                    tOpArr.loc[date, key] = (tFlow_ave + tFlow_next[key]) * (1 - math.exp(-24 / tLag)) * 0.1 * \
                                            area_subs[
                                                key] / 1000 / 3600 / 24  # Calculate the tile flow reaching the discharge sites, in cms
                    tFlow_next[key] = (tFlow_ave + tFlow_next[key]) * (1 - (1 - math.exp(
                        -24 / tLag)) * 0.1)  # Calculate the tile flow pool for the next simulation day
                    del current_array
                    del tFlow_ave
                del key
                del value
            else:
                for (key, value) in subwtshd_dic.items():
                    current_array = np.where(value == 1, tFlow, np.NAN)
                    tFlow_ave = np.nanmean(current_array)
                    tOpArr.loc[date, key] = (tFlow_ave + tFlow_next[key]) * (1 - math.exp(-24 / tLag)) * (
                            0.1 + 0.18 * TmpSoil) * area_subs[
                                                key] / 1000 / 3600 / 24  # Calculate the tile flow reaching the discharge sites, in cms
                    tFlow_next[key] = (tFlow_ave + tFlow_next[key]) * (1 - (1 - math.exp(-24 / tLag)) * (
                            0.1 + 0.18 * TmpSoil))  # Calculate the tile flow pool for the next simulation day
                    del current_array
                    del tFlow_ave
                del key
                del value
            del tFlow
            del wtrDepth

        # Clean up temporary numpy arrays, to release memory
        del ET_act
        del ET_soil
        del PET_soil
        del PET
        del S
        del M
        del Fd_m
        if prcp_d.loc[date] > 0:
            del F_Ia
            del ET_can
            del prcp
            del Fc
            del Ia
            del Fd
            del q
            del Fc0
            del c_Ia

        # Calculate the travel time of surface flow
        if qm_ds != None:
            qm_ds = None
            # Prepare flow rate for travel time calculation
            qv = qm / 3600000 / tGen  # Calculate overland flow rate, in m/s
            qv_ds = gdal.GetDriverByName("GTiff").CreateCopy(tempFolder + "/qv.tif", zero_ds, strict=0)
            qv_ds.GetRasterBand(1).WriteArray(qv)
            qv_ds = None
            zero_absorption_ds = gdal.GetDriverByName("GTiff").CreateCopy(tempFolder + "/zero_absorption.tif", zero_ds,
                                                                          strict=0)
            zero_absorption_ds = None
            routing.route_flux(tempFolder + "/fdr_m.tif", fdr_uri, tempFolder + "/qv.tif",
                               tempFolder + "/zero_absorption.tif", tempFolder + "/loss.tif",
                               tempFolder + "/qv_acc.tif", 'flux_only')
            # os.remove(tempFolder+"/qv.tif")
            # os.remove(tempFolder+"/zero_absorption.tif")
            # os.remove(tempFolder+"/loss.tif")
            qv_acc_ds = gdal.Open(tempFolder + "/qv_acc.tif", gdal.GA_ReadOnly)
            qv_acc = qv_acc_ds.ReadAsArray()
            qv_acc_ds = None
            # os.remove(tempFolder+"/qv_acc.tif")
            qv1 = np.where(stream == 1, qv_acc,
                           qv)  # Calculate in-channel flow rate, and merge the two rate in one array
            ci4ri = np.where(zero_arr != 0, np.NAN, np.where(qv1 < 0.000000001, 0.000000001,
                                                             qv1))  # Convert 0 rate into the smallest value, preventing 0 as divisor
            # Calculate travel time of surface runoff across a grid cell, in seconds
            v = np.where(water == 1, v_lake, np.where(stream == 1,
                                                      np.power(slp_v, 0.3) * np.power(ci4ri * (cellSize ** 2), 0.4) / (
                                                              np.power(n_Mnng, 0.6) * np.power(strWidth, 0.4)),
                                                      np.power(slp_v, 0.3) * np.power(ci4ri, 0.4) * np.power(length,
                                                                                                             0.4) / np.power(
                                                          n_Mnng, 0.6)))
            t = length / v
            v_ds = gdal.GetDriverByName("GTiff").CreateCopy(tempFolder + "/v_reverse.tif", zero_ds, strict=0)
            v_ds.GetRasterBand(1).WriteArray(1 / v)
            v_ds = None
            t_ds = gdal.GetDriverByName("GTiff").CreateCopy(outputGdb + '/t%s.tif' % date, zero_ds, strict=0)
            t_ds.GetRasterBand(1).WriteArray(t)
            t_ds = None
            # Calculate the cumulative travel time, in hours
            start_time0 = time.time()
            routing.distance_to_stream(fdr_uri, outputGdb + "/outlet_ras.tif", outputGdb + '/tCon%s.tif' % date,
                                       tempFolder + "/v_reverse.tif")
            print("--- %s seconds1 ---" % (time.time() - start_time0))
            # os.remove(tempFolder+"/v_reverse.tif")
            flowTime_ds = gdal.Open(outputGdb + '/tCon%s.tif' % date, gdal.GA_Update)
            flowTime = flowTime_ds.ReadAsArray()
            flowTime_ndv = flowTime_ds.GetRasterBand(1).GetNoDataValue()
            tCon = np.where(flowTime != flowTime_ndv, flowTime / 3600, flowTime_ndv)
            flowTime_ds.GetRasterBand(1).WriteArray(tCon)
            flowTime_ds = None
            del flowTime
            del tCon
            del t
            del v
            del ci4ri
            del qv1
            del qv_acc
            del qv
            del qm
            del tGen

        # Complete the hydrologic simulation of one day, and continue the next day
        date_n += 1

        if date_n % 10 == 0:
            print 'Day %s simulated.' % date

    # Close output files for parameters
    parameters.close()
    del parameters

    # Write the base flow (bOpArr) out in a file
    bOpArr.to_csv(bFlow_File, header=True, index=True, index_label="date", float_format='%.4f', sep='\t', mode='a')

    # Write the tile flow (rOpArr) out in a file, if tile flow module is active
    if tile == True:
        tOpArr.to_csv(tFlow_File, header=True, index=True, index_label="date", float_format='%.4f', sep='\t', mode='a')

    # os.remove(outputGdb+"/outlet_ras.tif")
    del length
    del landuse_arr
    del zero_arr
    del soilHG
    del soil_z
    del soil_Pe
    del soil_FC
    del soil_vlm
    del water
    del stream
    del landuseTile
    del strWidth
    del n_Mnng
    del Fc0_normal
    del Fc0_winter
    del S1
    del slp_v
    del k_tDrain

    print 'Simulation finished, start routing.'

    """Calculate the surface flow that reaches the watershed outlet for a specific day"""
    # Create a pandas DataFrame to store surface flow that reach the discharge sites, in cms
    qOpArr = pd.DataFrame(np.zeros((len(dates), len(discharge_dic)), dtype=np.float32), dates,
                          columns=discharge_dic.keys())
    date_n = dates.get_loc(dayRouting)
    while date_n < len(dates):
        progressCheck = round(progressCheck + 50.0 / len(dates), 2)
        progressBar(progress, label, progressCheck)
        # Prepare a string representing the simulating date
        date = str(dates[date_n].year * 10000 + dates[date_n].month * 100 + dates[date_n].day)
        # Calculate and write out surface flow that reach the monitoring gauges each day
        qOutput.write(str(dates[date_n].year) + '-' + str(dates[date_n].month) + '-' + str(dates[date_n].day) + '\t')
        # Initiate a dictionary to temporarily store rasters that representing cummulative surface runoff reaching the discharge sites, in mm
        qOp_dic = {}
        for (key, subwtshd) in subwtshd_dic.items():
            qOp_dic[key] = np.where(subwtshd == 1, 0.0, np.NAN)
        del key
        del subwtshd
        x = 1
        while x <= 7:
            date_x = str(dates[date_n - x + 1].year * 10000 + dates[date_n - x + 1].month * 100 + dates[
                date_n - x + 1].day)  # Prepare a string representing the date (x-1) days before the simulatiing day
            if os.path.isfile(outputGdb + '/q%s.tif' % date_x):
                q_ds = gdal.Open(outputGdb + '/q%s.tif' % date_x, gdal.GA_ReadOnly)
                if q_ds != None:
                    # Read surface flow raster q in numpy array
                    q_arr = q_ds.ReadAsArray()
                    q_ds = None
                    # Read cummulative travel time tCon in numpy array
                    tCon_ds = gdal.Open(outputGdb + '/tCon%s.tif' % date_x, gdal.GA_ReadOnly)
                    tCon_arr = tCon_ds.ReadAsArray()
                    tCon_ds = None
                    # Prepare Tsub_dic
                    Tsub_dic = {}
                    for (key,
                         value) in discharge_dic.items():  # Sample the tCon raster with given discharge sites (sitesDischarge)
                        Tsub_dic[key] = tCon_arr[value[0], value[1]]
                    del key
                    del value
                    for (key,
                         subwtshd) in subwtshd_dic.items():  # Prepare adjusted cummulative travel time raster by subtracting T_sub from the original tCon raster
                        T_sub = Tsub_dic[key]
                        tCon_mod = np.where(subwtshd == 1, tCon_arr - Tsub_dic[key], np.NAN)
                        qOp_dic[key] = np.where((tCon_mod <= 24 * x - 12) & (tCon_mod > 24 * x - 36),
                                                qOp_dic[key] + q_arr, qOp_dic[key])
                    del Tsub_dic
                    del key
                    del subwtshd
                    del q_arr
                    del tCon_arr
                    del tCon_mod
                else:
                    del q_ds
            x += 1
        for (key, qOp) in qOp_dic.items():
            qOp_ave = np.nanmean(qOp) * area_subs[key] / 1000 / 3600 / 24  # in cms
            qOpArr.loc[date, key] = qOp_ave  # Store result in the pandas dataframe
            qOutput.write('%.4f\t' % qOp_ave)  # Write result in the text file for surface flow output
            del qOp_ave
        del key
        del qOp
        del qOp_dic
        qOutput.seek(-1, 1)
        qOutput.truncate()
        qOutput.write('\n')

        # Calculate and write out total flow
        if tile == True:
            fOp = bOpArr.loc[date] + qOpArr.loc[date] + tOpArr.loc[date]
        else:
            fOp = bOpArr.loc[date] + qOpArr.loc[date]
        fOutput.write(str(dates[date_n].year) + '-' + str(dates[date_n].month) + '-' + str(dates[date_n].day) + '\t')
        for key in discharge_dic.keys():
            fOutput.write('%.4f\t' % fOp[key])
        del key
        fOutput.seek(-1, 1)
        fOutput.truncate()
        fOutput.write('\n')
        del fOp

        # Continue the next day
        date_n += 1

        if date_n % 10 == 0:
            print 'Day %s finished.' % date

    # Close output files for surface flow and total flow
    del qOpArr
    qOutput.close()
    del qOutput
    fOutput.close()
    del fOutput
    zero_ds = None
    # os.remove(outputGdb+"/zero_raster.tif")

    # shutil.rmtree(tempFolder)
    progressBar(progress, label, 100)

    print 'Voila! DHM-WM local water balance routine has completed your task.'
    print("--- %s seconds ---" % (time.time() - start_time))


def start(root11):
    folderPath = None
    print("working")
    global frame, frame21, frame22, frame3, filenames, rowno, value
    global root1, canvas
    global root, frame, frame21, frame22
    root1 = Toplevel(root11)
    root1.title("DHM-WM")
    root1.resizable(width=True, height=True)
    root1.geometry("1200x800")

    canvas = Canvas(root1, height=1200, width=2000, bg="White", highlightbackground="gray", highlightcolor="gray",
                    highlightthickness=3, )

    frame = Frame(canvas, borderwidth=5, width=450, height=800, bg="White", highlightbackground="gray",
                  highlightcolor="gray", highlightthickness=3, )
    frame21 = Frame(canvas, borderwidth=5, width=300, height=800, bg="White", highlightbackground="gray",
                    highlightcolor="gray", highlightthickness=3, )
    frame22 = Frame(canvas, borderwidth=5, width=300, height=800, bg="White", highlightbackground="gray",
                    highlightcolor="gray", highlightthickness=3, )
    frame3 = Frame(canvas, borderwidth=5, width=500, height=800, bg="White", highlightbackground="gray",
                   highlightcolor="gray", highlightthickness=3, )
    frame.grid(row=0, column=0)
    frame21.grid(row=0, column=1)
    frame22.grid(row=0, column=2)
    frame3.grid(row=0, column=3)
    frame.grid_propagate(0)
    frame21.grid_propagate(0)
    frame22.grid_propagate(0)
    frame3.grid_propagate(0)
    canvas.grid()
    canvas.grid_propagate(0)

    global haveDailyKc, haveDailyPET, haveDisPrcp
    haveDailyKc = False
    haveDailyPET = False
    haveDisPrcp = False
    filenames = ["Raster", "Vector", "Text"]
    rowno = 3
    value = False
    folderPath = setDestination()
    buttonFolder = Button(frame,text="Set Destination Folder", command=setDestination, width=20 ).grid(row=0, column=0, sticky="W")
    buttonr = Button(frame, text="display", command=displayShapefile, width=20).grid(row=0, column=1, sticky="W")
    root1.mainloop()

# root11.withdraw()

# start(root11)
