##########################################################################################
# Dependencies
##########################################################################################
import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

# Print event statistics?
doPrint = False

# Where is event data?
caseID = "slabtest1"
dirIN  = "/Projects/HydroMet/dswales/CMIP6/events/"+caseID+"/"

# Which duration events to plot?
persistence = 24

# Which models to include?
# All models
models = ["ACCESS-ESM1-5","CMCC-CM2-SR5","CMCC-ESM2","CanESM5","CNRM-CM6-1","CNRM-ESM2-1",\
          "HadGEM3-GC31-LL","MPI-ESM-1-2-HAM","MPI-ESM1-2-HR","MPI-ESM1-2-LR","UKESM1-0-LL"]
# Models with both historical/future data available
models = ["CMCC-CM2-SR5","CMCC-ESM2","CanESM5","MPI-ESM1-2-LR"]

# Which future scenario to use?
scn = "ssp370"#"ssp245"#"ssp126"#"ssp585"

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
if doPrint: print("-----------------------------------------------------")
if doPrint: print("MODEL                SCENARIO     PERCENTILE   EVENTS")
if doPrint: print("-----------------------------------------------------")
for file in sorted(os.listdir(dirIN)):
    if file.endswith(str(persistence)+".nc"):
        file_list.append(file)
        dataset  = xr.open_dataset(dirIN+file)
        model    = np.append(model,str(dataset.model.values))
        scenario = np.append(scenario,str(dataset.scenario.values))
        ptile    = np.append(ptile,float(dataset.percentile.values)*100.)
        nevent   = np.append(nevent,dataset.dims["event"])
        if doPrint: print(model[count].ljust(20),scenario[count].ljust(12),str(int(ptile[count])).zfill(2).ljust(12),nevent[count])
        count = count + 1
if doPrint: print("-----------------------------------------------------")

# Plot configuration
xrange = [min(ptile), max(ptile)]
yrange = [0,max(nevent)/30.]

# Plot
fig = plt.figure(figsize=(10,8))
plotOUT = dirOUT+"event_stats.p"+str(persistence)+"."+scn+".png"
print("Output file: ",plotOUT)
#
# Historical
#
plt.subplot(2,1,1)
for imodel in models:
    mi = np.where((imodel == model) & ('historical' == scenario))[0]
    plt.plot(ptile[mi],nevent[mi]/30.)
plt.ylabel("Events/Season (#)")
plt.ylim(yrange)
plt.xlim(xrange)
plt.xticks(color='w')
plt.title("Historical")
plt.legend(models,loc='lower left',fontsize='xx-small')

#
# Future - Historical
#
plt.subplot(2,1,2)
for imodel in models:
    mih = np.where((imodel == model) & ('historical' == scenario))[0]
    mif = np.where((imodel == model) & (scn == scenario))[0]
    if (np.any(mif)):
        if len(mif) == len(mih):
            plt.plot(ptile[mif],(nevent[mif]-nevent[mih])/30.)
plt.plot(xrange,[0,0],color='grey',linestyle='dotted')
plt.xlabel("Strength (percentile)")
plt.ylabel("Events/Season (#)")
plt.title("Future("+scn+") - Historical")
plt.xlim(xrange)
plt.ylim([-3,3])
plt.savefig(plotOUT)
plt.show()

##########################################################################################
# NO CHANGES BELOW
##########################################################################################
