##########################################################################################
# Dependencies
##########################################################################################
import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
########################################################################################## 
########################################################################################## 
debug      = False
print_diag = True#False
dohist     = True

# Slab loaction
dirIN = "/Projects/HydroMet/dswales/CMIP6/slabs/slabtest1/"

# What is the model's temporal resolution? (in hours)
timestep = 3

# Output location?
caseID = "slabtest1"
dirOUT = "/Projects/HydroMet/dswales/CMIP6/events/"+caseID+"/"
if(not os.path.isdir(dirOUT)): os.mkdir(dirOUT)

##########################################################################################
# Event detection configuration
##########################################################################################

# Which percentile (strength) for IVT anomaly?
ptiles = np.linspace(.80,.99,20)

# How long (duration) does IVT anomaly persist along coast(slb)? (in hours)
persistences = [24,36]

# Which years?
if (dohist):
    years = [1980,2010]
else:
    years = [2070,2100]
    
##########################################################################################
# NO CHANGES NEEDED BELOW
##########################################################################################
# Use all of the netcdf files in dirIN.
file_list_future = []
file_list_hist   = []
for files in os.listdir(dirIN):
    if files.endswith("historical.nc"):
        file_list_hist.append(files)
    else:
        file_list_future.append(files)
if (dohist):
    file_list = file_list_hist
else:
    file_list = file_list_future

if debug:
    print("IN DEBUG MODE")
    file_list    = [file_list[0]]
    ptiles       = [0.95]
    persistences = [24]
    
# Process each file...
for file in file_list:
     # Load data
     ds     = xr.open_dataset(dirIN+file)
     data   = ds.sel(time=slice(str(years[0]), str(years[1])))
     IVT    = data.IVT.values
     CDF    = data.CDF.values
     PDF    = data.bin.values
     time   = data.time.values
     lat    = data.lat.values
     lon    = data.lon.values
     npts   = data.lat.size
     ntimes = data.time.size
     
     #####################################################################################
     # BEGIN EVENT DETECTION
     #####################################################################################
     for persistence in persistences:
         for ptile in ptiles:
             # Create "instantaneous event mask" (All instances of IVT exceeeding "ptile")
             inst_evt_msk = np.full((npts,ntimes),False,dtype='bool')
             for ipt in range(0,npts):
                 ivtT = np.interp(ptile, CDF[ipt,:], PDF)
                 inst_evt_msk[ipt,np.where(IVT[:,ipt] > ivtT)] = True
             
             # Step through instantaneous events and apply persistence threshold across the
             # entire slab.
             flag1             = False
             event_length      = 0
             nevents           = 0
             event_year_begin  = []
             event_month_begin = []
             event_day_begin   = []
             event_hour_begin  = []
             event_year_end    = []
             event_month_end   = []
             event_day_end     = []
             event_hour_end    = []
             for itime in range(0,ntimes):
                 # Is there an instantaneous-event anywhere across the slab?
                 if (np.any(inst_evt_msk[:,itime])):
                     # Average location of anomaly (not used)
                     xi   = np.where(inst_evt_msk[:,itime])
                     lati = np.mean(lat[xi])
                     loni = np.mean(lon[xi])

                     # Is this the first instantaneous-event detected? (If so, save index)
                     if (event_length == 0): event_start = itime

                     # How long have we been in this event?
                     event_length = event_length + timestep

                     # Have we observed subsequent instantaeous events long enough to satisfy
                     # the requested persistence threshold?
                     if (event_length >= persistence):
                         flag1      = True
                         event_stop = itime
                 #
                 # If not in an event...
                 #
                 else:
                     # If just exited event, save information
                     if (flag1):
                         nevents = nevents + 1
                         event_year_begin.append( data.time.dt.year[ event_start].values)
                         event_month_begin.append(data.time.dt.month[event_start].values)
                         event_day_begin.append(  data.time.dt.day[  event_start].values)
                         event_hour_begin.append( data.time.dt.hour[ event_start].values)
                         event_year_end.append(  data.time.dt.year[  event_stop].values)
                         event_month_end.append( data.time.dt.month[ event_stop].values)
                         event_day_end.append(   data.time.dt.day[   event_stop].values)
                         event_hour_end.append(  data.time.dt.hour[  event_stop].values)
                     # Reset flags.
                     flag1        = False
                     event_length = 0

             # Write to output
             modelname = str(file)[0:file.find('_IVT')]
             scenario  = str(file)[file.find('IWV_')+4:file.find('.nc')]
             fileOUT   = dirOUT+"events."+modelname+"."+scenario+".p"+str(int(ptile*100)).zfill(2)+".d"+str(persistence).zfill(2)+".nc"
             year_start_OUT  = xr.Dataset({"year_start": (("event"), event_year_begin)})
             year_end_OUT    = xr.Dataset({"year_end":   (("event"), event_year_end)})
             month_start_OUT = xr.Dataset({"month_start":(("event"), event_month_begin)})
             month_end_OUT   = xr.Dataset({"month_end":  (("event"), event_month_end)})
             day_start_OUT   = xr.Dataset({"day_start":  (("event"), event_day_begin)})
             day_end_OUT     = xr.Dataset({"day_end":    (("event"), event_day_end)})
             hour_start_OUT  = xr.Dataset({"hour_start": (("event"), event_hour_begin)})
             hour_end_OUT    = xr.Dataset({"hour_end":   (("event"), event_hour_end)})
             model_OUT       = xr.Dataset({"model":      modelname})
             scenario_OUT    = xr.Dataset({"scenario":   scenario})
             ptile_OUT       = xr.Dataset({"percentile": ptile})
             xr.merge([year_start_OUT, year_end_OUT, month_start_OUT, month_end_OUT, \
                       day_start_OUT,  day_end_OUT,  hour_start_OUT,  hour_end_OUT,\
                       model_OUT, scenario_OUT, ptile_OUT]).to_netcdf(fileOUT)

             if (print_diag):
                 print("------------------------------------------------------------")
                 print("Model:            ",modelname)
                 print("Input slab file:  ",dirIN+file)
                 print("Description:      ")
                 print("   Time range:    ",str(years[0])+":"+str(years[1]))
                 print("   Percentile:    ",str(ptile*100.))
                 print("   Duration:      ",str(persistence))
                 print("   # of events:   ",nevents)
                 print("Output written to ",fileOUT )
                 #for ievent in range(0,nevents-1):
                 #    print("       "+\
                 #          str(event_year_begin[ievent]).zfill(4)  + "/"   + \
                 #          str(event_month_begin[ievent]).zfill(2) + "/"   + \
                 #          str(event_day_begin[ievent]).zfill(2)   + ":"   + \
                 #          str(event_hour_begin[ievent]).zfill(2)  + "Z - "+ \
                 #          str(event_year_end[ievent]).zfill(4)    + "/"   + \
                 #          str(event_month_end[ievent]).zfill(2)   + "/"   + \
                 #          str(event_day_end[ievent]).zfill(2)     + ":"   + \
                 #          str(event_hour_end[ievent]).zfill(2)    + "Z")

# END PROGRAM
