"""This program is designed to generate point features from ascii files,
   and interpolate the point feature to generate grided precipitation by IDW.
   Created by Sisi Li,
   on March 13, 2016, and modified on June 26, 2017"""

"""
Note: Store the point precipitation data in ArcGIS ascii files (.xyz format).
Put these ascii files in a folder same with this script.
Name these ascii files as "prcp"+YYYY(year)+DDD(day of year)+".xyz", for example: prcp2003001.xyz.
These ascii files have three columns, x-coordinate, y-coordinate, and z values (precipitation in mm).
"""

import arcpy
from arcpy import env
from arcpy.sa import *
import pandas as pd

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("3D")

""" Set data sources """
prcp_d_File = "prcp_d.txt" # Set the file name of the watershed average daily precipitation data, put it in the same folder with the script
mask = "F:/DHM-WM/LREW_example/data_input/grids/fdr" # Set the mask for generating gridded precipitation data, usually fdr raster that has a spatial resolution of DHM-WM simulation
feature_Folder = "F:/DHM-WM/LREW_example/data_input/grids/prcp/point data/prcp_features" # Set a folder to store precipitation feature points data
raster_Folder = "F:/DHM-WM/LREW_example/data_input/grids/prcp" # Set a folder to store the output rasters of gridded precipitation

""" Set parameters """
# Set the start day and end day of processing period
startDay = "2003-1-1"
endDay = "2006-12-31"
# Set the extent for ascii to feature points analysis
pointExtent = "237786.0 3507136.0 249514.0 3517170.0"
# Set parameters for IDW analysis
cellSize = 30.0
power = 2
searchRadius = 4

""" Start analysis, usually no need to change contents below """
# Read in the watershed average daily precipitation data
prcp_d = pd.read_csv(prcp_d_File, sep='\t', header=0, index_col=0, squeeze=True, parse_dates=True)
# Prepare a pandas dates for processing period
dates = pd.date_range(startDay, endDay, None, 'D')

# Use a for loop to generate feature class for each day with rainfall more than 0mm
for date in dates:
    YearDay = str(date.year*1000 + date.dayofyear)
    dateStr = str(date.year*10000 + date.month*100 + date.day)
    if prcp_d[date] > 0:
        # Set environment for ASCII to feature points
        sr = arcpy.Describe(mask).spatialReference # Set the spatial reference as "NAD_1983_UTM_Zone_17N"
        arcpy.env.extent = pointExtent # Set the processing extent
        # ASCII to feature class
        inAsciiFile = "prcp"+YearDay+".xyz"
        outFeatureClass = feature_Folder+"/prcp"+dateStr+".shp"
        arcpy.ddd.ASCII3DToFeatureClass(inAsciiFile, "XYZ", outFeatureClass, "POINT", input_coordinate_system=sr)
        # Set environment for IDW
        arcpy.env.extent = mask
        arcpy.env.mask = mask
        # Do IDW
        outRaster = raster_Folder+"/prcp"+dateStr
        arcpy.ddd.Idw(outFeatureClass, 'Shape.Z', outRaster, cellSize, power, searchRadius)

arcpy.CheckInExtension("3D")

        
