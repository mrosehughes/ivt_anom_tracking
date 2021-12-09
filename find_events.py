##########################################################################################
# Dependencies
##########################################################################################
import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

debug = False

# Slab loaction
dirIN = "/Projects/HydroMet/dswales/CMIP6/slabs/slabtest0/"

# How many files to process?
file_list = []
for files in os.listdir(dirIN):
    if files.endswith(".nc"):
        file_list.append(files)
if (debug): file_list = [file_list[0]]
nfiles = len(file_list)

# IVT PDF configurations
nbins = 150
ivtR  = [0,1500]

# Process each file...
init = True
for ifile in range(0,nfiles):
     print("CMIP6 slab file:       ",dirIN+file_list[ifile])
     modelname = str(file_list[ifile])[0:file_list[ifile].find('_IVT')]

     # Load data
     data  = xr.open_dataset(dirIN+file_list[ifile])
     nlon  = data.lon.size
     nlat  = data.lat.size
     ntime = data.time.size
     ivt   = data.IVT.values
     if (init):
         pdf  = np.zeros((nfiles,nlat,nbins))
         cdf  = np.zeros((nfiles,nlat,nbins))
         init = False
     
     # 
     for ipt in range(0,nlat):
         # Create PDF/CDFs of IVT 
         p, bins = np.histogram(ivt[:,ipt], bins=nbins, range=ivtR)
         cdf[ifile,ipt,:] = np.cumsum(p)/np.sum(p)
         pdf[ifile,ipt,:] = p
