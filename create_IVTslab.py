##########################################################################################
# Dependencies
##########################################################################################
import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
##########################################################################################
# Routine to search array (arry) for closet value to K, returns index.
##########################################################################################
def closest(arry, K):
     return (np.abs(arry - K)).argmin()

##########################################################################################
##########################################################################################
# Where are the CMIP6 IVT files to process?
data_dir = "/Projects/HydroMet/dswales/CMIP6/IVT/"

# What are the lon/lats for the slab?
lon_slab = np.array([233.00, 234.25, 235.50, 235.50, 235.50, 235.50, 235.50 ],dtype='float')
lat_slab = np.array([ 50.00,  48.75,  46.25,  45.50,  44.50,  43.25,  42.00 ],dtype='float')

# Configuration from WRF 25km data.
#lon_slab = np.array([-127.00, -126.25, -125.50, -124.75, -124.60, -124.40, -124.20,\
#            -124.00, -124.00, -124.10, -124.15, -124.00, -124.15, -124.25,\
#            -124.25, -124.25, -124.25, -124.00, -124.25, -124.00, -124.00,\
#            -124.00, -123.75, -123.50, -123.00, -122.50, -122.00, -122.00,\
#            -121.50, -121.00, -120.50, -120.50, -119.00, -118.00, -117.00,\
#                     -117.00, -117.00, -116.50],dtype='float')+360
#lat_slab = 50. - np.linspace(0,len(lon_slab),num=len(lon_slab))*0.5

# ID for slab configuration? (to create output file directory)
caseID = 'slabtest0'

# Where to store output files?
dirOUT = "/Projects/HydroMet/dswales/CMIP6/slabs/"+caseID+"/"
if(not os.path.isdir(dirOUT)): os.mkdir(dirOUT)

debug    = True#True
doPlot   = True#True
showPlot = False#True
##########################################################################################
# NO CHANGES NEEDED BELOW
##########################################################################################

# Number of slab points to extract
npts_slab = len(lat_slab)
if (npts_slab != len(lon_slab)):
     print("ERROR: Slab lon/lat size are inconsistent.")
     exit()

# Get file list
files  = os.listdir(data_dir)
nfiles = len(files)

# Process each file
for ifile in range(0,nfiles):
     print("CMIP6 file:       ",data_dir+files[ifile])
     modelname = str(files[ifile])[0:files[ifile].find('_IVT')]
     
     # Load CMIP6 data
     data  = xr.open_dataset(data_dir+files[ifile])
     nlon  = data.lon.size
     nlat  = data.lat.size
     ntime = data.time.size

     # For debug mode, only need geodata for slab construction/plotting.
     if (debug): ntime=1
     
     # Find the nearest model grid points for requested slab, pull out IVT.
     loni    = np.empty((npts_slab),dtype='int')
     lati    = np.empty((npts_slab),dtype='int')
     IVTslab = np.empty((ntime,npts_slab),dtype='float')
     for islab in range(0,npts_slab):
          loni[islab] = closest(data.lon.values, lon_slab[islab])
          lati[islab] = closest(data.lat.values, lat_slab[islab])
          IVTslab[:,islab] = data["IVT"][0:ntime, lati[islab], loni[islab]].values
          # Add check/warning for cases when the provided slab has redundant points (e.g. in
          # the case when the slab requested is on a finer grid than the CMIP6 data)
          if (debug):
               for itest in range(0,islab):
                    if (loni[islab] == loni[itest] and lati[islab] == lati[itest]):
                         print("------------------------------------------------------------------------------------------")
                         print("WARNING: Redundant slab points have been found.")
                         print("Current slab index: "+str(islab)+" is identical to previous slab index: "+str(itest))
                         print("["+str(data.lon[loni[islab]].values)+","+str(data.lat[lati[islab]].values)+"]")

     # Create output file
     if (not debug):
          fileOUT = dirOUT+files[ifile]
          print("Output slab file: ",fileOUT)
          ivtOUT = xr.Dataset({"IVT": (("time", "slab"),IVTslab)},        \
                              coords = {"time": data.time[0:ntime].values,\
                                        "slab": np.linspace(1,npts_slab,npts_slab)})
          latOUT = xr.Dataset({"lat":(("slab"),data.lat[lati].values)},   \
                              coords = {"slab": np.linspace(1,npts_slab,npts_slab)})
          lonOUT = xr.Dataset({"lon":(("slab"),data.lon[loni].values)},   \
                              coords = {"slab": np.linspace(1,npts_slab,npts_slab)})
          xr.merge([ivtOUT,latOUT,lonOUT]).to_netcdf(fileOUT)
     
     # Plot the locations of the slabs on map?
     if (doPlot):
          plotOUT = dirOUT+"slab."+modelname+".png"
          print("Slab domain plot: ",plotOUT)
          fig=plt.figure(figsize=(8, 6))
          m = Basemap(llcrnrlon=-130.,llcrnrlat=20.,urcrnrlon=-110.,urcrnrlat=52.)#,projection='merc')
          m.drawcoastlines()
          m.drawcountries()
          m.drawstates()
          x,y = m(data.lon[loni].values-360,data.lat[lati].values)
          m.plot(x,y, 'bo', markersize=4)
          plt.savefig(plotOUT)
          if (showPlot): plt.show()
