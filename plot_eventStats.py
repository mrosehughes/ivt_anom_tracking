##########################################################################################
# Dependencies
##########################################################################################
import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

# Where is event data?
caseID = "slabtest1"
dirIN  = "/Projects/HydroMet/dswales/CMIP6/events/"+caseID+"/"

# Which duration events to plot?
persistence = 24

# Which models to include?
models = ["ACCESS-ESM1-5","CMCC-CM2-SR5","CMCC-ESM2","CanESM5","CNRM-CM6-1","CNRM-ESM2-1",\
          "HadGEM3-GC31-LL","MPI-ESM-1-2-HAM","MPI-ESM1-2-HR","MPI-ESM1-2-LR","UKESM1-0-LL"]

# Which future scenario to use?
scn = "ssp126"

# Where to store plots?
dirOUT = dirIN+"plots/"
if(not os.path.isdir(dirOUT)): os.mkdir(dirOUT)

# Read in event statistics...
file_list = []
model     = np.array([],dtype='str')
scenario  = np.array([],dtype='str')
nevent    = np.array([],dtype='int') 
ptile     = np.array([],dtype='float')
count     = 0
print("-----------------------------------------------------")
print("MODEL                SCENARIO     PERCENTILE   EVENTS")
print("-----------------------------------------------------")
for file in sorted(os.listdir(dirIN)):
    if file.endswith(str(persistence)+".nc"):
        file_list.append(file)
        dataset  = xr.open_dataset(dirIN+file)
        model    = np.append(model,str(dataset.model.values))
        scenario = np.append(scenario,str(dataset.scenario.values))
        ptile    = np.append(ptile,float(dataset.percentile.values))
        nevent   = np.append(nevent,dataset.dims["event"])
        print(model[count].ljust(20),scenario[count].ljust(12),str(int(ptile[count]*100)).zfill(2).ljust(12),nevent[count])
        count = count + 1

# Plot configuration
xrange = [min(ptile), max(ptile)]
yrange = [0,40]

# Plot
fig = plt.figure(figsize=(8,6))
plotOUT = dirOUT+"event_stats.p"+str(persistence)+"."+scn+".png"
print(plotOUT)
#
# Historical
#
plt.subplot(2,1,1)
for imodel in models:
    mi = np.where((imodel == model) & ('historical' == scenario))[0]
    plt.plot(ptile[mi],nevent[mi]/30.)
plt.xlabel("Strength (percentile)")
plt.ylabel("Events/Season (#)")
plt.ylim(yrange)
plt.xlim(xrange)
plt.savefig(plotOUT)
plt.show()

##########################################################################################
# NO CHANGES BELOW
##########################################################################################
