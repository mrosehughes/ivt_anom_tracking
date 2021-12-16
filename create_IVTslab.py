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
debug    = True
doPlot   = True
showPlot = True
##########################################################################################

# Where are the CMIP6 IVT files to process?
data_dir  = "/Projects/HydroMet/dswales/CMIP6/IVT/"
lsmsk_dir = "/Projects/HydroMet/mhughes/CMIP6IVTdataout/landmasks/"

# Use all of the files.
files  = os.listdir(data_dir)
#if (debug): files = [files[0]]
nfiles = len(files)

# ID for slab configuration? (to create output file directory)
#caseID = 'slabtest0'
# What are the lon/lats for the slab?
#lon_slab = np.array([233.00, 234.25, 235.50, 235.50, 235.50, 235.50, 235.50 ],dtype='float')
#lat_slab = np.array([ 50.00,  48.75,  46.25,  45.50,  44.50,  43.25,  42.00 ],dtype='float')

# ID for slab configuration? (to create output file directory)
caseID = 'slabtest1' #extend south and start moving east
# What are the lon/lats for the slab?
lon_slab = np.array([233.00, 234.25, 235.50, 235.50, 235.50, 235.50, 235.50,\
                     235.50, 236.00, 236.00, 236.50, 236.50, 237.00, 237.00,\
                     237.50, 237.50, 238.00, 238.00, 238.50, 238.50, 239.00],dtype='float')
lat_slab = np.array([ 50.00, 49.00, 48.00, 47.00, 46.00, 45.00, 44.00, \
                      43.00, 42.00, 41.00, 40.00, 39.00, 38.00, 37.00, \
                      36.00, 35.00, 34.00, 33.00, 32.00, 31.00, 30.00 ],dtype='float')

# ID for slab configuration? (to create output file directory)
#caseID = 'slabtest2' #extend south and start moving east
# What are the lon/lats for the slab?
#lon_slab = np.array([232.00, 234.25, 235.50, 235.50, 235.50, 235.50, 235.50,\
#                     235.50, 235.50, 235.50, 235.50, 236.00, 236.00, 236.50,\
#                     237.00, 237.50, 238.00, 238.50, 239.00, 239.50, 240.00],dtype='float')
#lat_slab = np.array([ 50.00, 49.00, 48.00, 47.00, 46.00, 45.00, 44.00, \
#                      43.00, 42.00, 41.00, 40.00, 39.00, 38.00, 37.00, \
#                      36.00, 35.00, 34.00, 33.00, 32.00, 31.00, 30.00 ],dtype='float')

# Where to store output files?
dirOUT = "/Projects/HydroMet/mhughes/CMIP6IVTdataout/slabs/"+caseID+"/"
if(not os.path.isdir(dirOUT)): os.mkdir(dirOUT)

# IVT PDF configuration. (Written to output slab file)
nbins     = 150
ivtRange  = [0,1500] # (kg/m/s)

##########################################################################################
# NO CHANGES NEEDED BELOW
##########################################################################################

# Number of slab points to extract
npts_slab = len(lat_slab)
if (npts_slab != len(lon_slab)):
     print("ERROR: Slab lon/lat size are inconsistent.")
     exit()

# Landmask files
lsmsk_file_list = []
for lsmskfiles in os.listdir(lsmsk_dir):
     if lsmskfiles.endswith(".nc"):
          lsmsk_file_list.append(lsmskfiles)
     
# Process each file
for ifile in range(0,nfiles):
     print("CMIP6 file:       ",data_dir+files[ifile])
     modelname = str(files[ifile])[0:files[ifile].find('_IVT')]
     
     # Load CMIP6 data
     data  = xr.open_dataset(data_dir+files[ifile])
     nlon  = data.lon.size
     nlat  = data.lat.size
     ntime = data.time.size

     # Search for landmask file
     found_lsmask_file = False
     for file_lsmsk in lsmsk_file_list:
          if modelname in file_lsmsk:
               lsmsk_file        = lsmsk_dir + file_lsmsk
               found_lsmask_file = True
     if (not found_lsmask_file):
          print("ERROR: No landmask file found for "+modelname+" Skipping...")
          break
     else:
          print("lsmsk_file:       ",lsmsk_file)

     # Read in landmask file
     data_lsmsk = xr.open_dataset(lsmsk_file)
     lat_lsmsk = data_lsmsk.lat.values
     lon_lsmsk = data_lsmsk.lon.values
     lsmsk     = data_lsmsk.sftlf.values
     
     # Indices (cool_season) for (mi) months
     mi          = [1,2,3,10,11,12]
     cool_season = np.array([],dtype='int')
     for im in range(0,5):
          cool_season =  np.append(cool_season, np.where(data.time.dt.month == mi[im]))

     # For debug mode, only need geodata for slab construction/plotting.
     if (debug): ntime=1
     
     # Find the nearest model grid points for requested slab, pull out IVT.
     loni    = np.empty((npts_slab),       dtype='int')
     loniu   = np.empty((npts_slab),       dtype='int')
     lati    = np.empty((npts_slab),       dtype='int')
     IVTslab = np.empty((ntime,npts_slab), dtype='float')
     PDFslab = np.empty((npts_slab,nbins), dtype='float')
     CDFslab = np.empty((npts_slab,nbins), dtype='float')
     for islab in range(0,npts_slab):
          loni[islab]  = closest(data.lon.values, lon_slab[islab])
          lati[islab]  = closest(data.lat.values, lat_slab[islab])
          loniu[islab] = loni[islab]
          # Check to ensure that slab-point is over ocean, if no then nudge west.
          lsmsk_local = lsmsk[closest(lat_lsmsk,lat_slab[islab]),closest(lon_lsmsk,lon_slab[islab])]
          if (lsmsk_local > 50):
               print("------------------------------------------------------------------------------------------")
               print("WARNING: The closest "+modelname+" grid-point is mostly over land. Moving West...")
               print("Land-fraction = ",lsmsk_local)
               print("Latitude      = ",data.lat[closest(data.lat.values,lat_slab[islab])].values)
               print("Longitude     = ",data.lon[closest(data.lon.values,lon_slab[islab])].values)
               loni[islab] = loni[islab]-1
          
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

     # Create PDF/CDFs of IVT (cool-season (ONDJFM) only). 
     if (not debug):
          p, bins = np.histogram(IVTslab[cool_season,islab], bins=nbins, range=ivtRange)
          CDFslab[islab,:] = np.cumsum(p)/np.sum(p)
          PDFslab[islab,:] = p

     # Create output file
     if (not debug):
          fileOUT = dirOUT+files[ifile]
          print("Output slab file: ",fileOUT)
          ivtOUT = xr.Dataset({"IVT": (("time", "slab"),IVTslab)},  \
                              coords = {"time": data.time.values,\
                                        "slab": np.linspace(1,npts_slab,npts_slab)})
          latOUT = xr.Dataset({"lat":(("slab"),data.lat[lati].values)},   \
                              coords = {"slab": np.linspace(1,npts_slab,npts_slab)})
          lonOUT = xr.Dataset({"lon":(("slab"),data.lon[loni].values)},   \
                              coords = {"slab": np.linspace(1,npts_slab,npts_slab)})
          cdfOUT = xr.Dataset({"CDF": (("slab", "bin"),CDFslab)},        \
                              coords = {"slab": np.linspace(1,npts_slab,npts_slab),\
                                        "bin":  0.5*(bins[0:nbins]+bins[1:nbins+1])})
          pdfOUT = xr.Dataset({"PDF": (("slab", "bin"),PDFslab)},        \
                              coords = {"slab": np.linspace(1,npts_slab,npts_slab),\
                                        "bin":  0.5*(bins[0:nbins]+bins[1:nbins+1])})
          xr.merge([ivtOUT,latOUT,lonOUT,cdfOUT,pdfOUT]).to_netcdf(fileOUT)
     
     # Plot the locations of the slabs on map?
     if (doPlot):
          if(not os.path.isdir(dirOUT+"plots/")): os.mkdir(dirOUT+"plots/")
          plotOUT = dirOUT+"plots/slab."+modelname+".png"
          print("Slab domain plot: ",plotOUT)
          fig=plt.figure(figsize=(8, 6))
          m = Basemap(llcrnrlon=-130.,llcrnrlat=20.,urcrnrlon=-110.,urcrnrlat=52.)#,projection='merc')
          m.drawcoastlines()
          m.drawcountries()
          m.drawstates()
          x,y = m(data.lon[loniu].values-360,data.lat[lati].values)
          m.plot(x,y, 'ro', markersize=4)
          x,y = m(data.lon[loni].values-360,data.lat[lati].values)
          m.plot(x,y, 'bo', markersize=4)
          plt.savefig(plotOUT)
          if (showPlot): plt.show()
