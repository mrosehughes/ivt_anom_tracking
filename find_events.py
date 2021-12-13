##########################################################################################
# Dependencies
##########################################################################################
import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

debug = True

# Slab loaction
dirIN = "/Projects/HydroMet/dswales/CMIP6/slabs/slabtest0/"

# Use all of the netcdf files in dirIN.
file_list = []
for files in os.listdir(dirIN):
    if files.endswith(".nc"):
        file_list.append(files)
if (debug): file_list = [file_list[0]]
nfiles = len(file_list)

# What is the model's temporal resolution? (in hours)
timestep = 3

# Event detection configuration
# Which percentile (strength) for IVT anomaly?
ptile = .90
# How long (duration) does IVT anomaly persist along coast(slb)? (in hours)
persistence = 24

##########################################################################################
# NO CHANGES NEEDED BELOW
##########################################################################################

# Process each file...
for ifile in range(0,nfiles):
     print("CMIP6 slab file:       ",dirIN+file_list[ifile])
     modelname = str(file_list[ifile])[0:file_list[ifile].find('_IVT')]

     # Load data
     data   = xr.open_dataset(dirIN+file_list[ifile])
     IVT    = data.IVT.values
     CDF    = data.CDF.values
     PDF    = data.PDF.values
     time   = data.time.values
     npts   = data.lat.size
     ntimes = data.time.size
     
     #####################################################################################
     # BEGIN EVENT DETECTION
     #####################################################################################

     # What is the IVT values assoicated with the chosen percentile?
     ivtT = np.zeros((npts),dtype='float')
     for ipt in range(0,npts):
         ivtT[ipt] = np.interp(ptile, CDF[ipt,:], PDF[ipt,:])

     print(ivtT)
# END PROGRAM
