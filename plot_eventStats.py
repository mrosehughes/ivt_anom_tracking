##########################################################################################
# Dependencies
##########################################################################################
import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

# Where is event data?
dirIN = "/Projects/HydroMet/dswales/CMIP6/events/slabtest1/"

# Which duration events to plot?
persistence = 24

# Read in event statistics...
file_list = []
model     = []
scenario  = []
nevent    = []
ptile     = []
count     = 0
print("MODEL           SCENARIO   P  EVENTS")
for file in sorted(os.listdir(dirIN)):
    if file.endswith(str(persistence)+".nc"):
        file_list.append(file)
        dataset = xr.open_dataset(dirIN+file)
        model.append(str(dataset.model.values))
        scenario.append(str(dataset.scenario.values))
        ptile.append(float(dataset.percentile.values))
        nevent.append(dataset.dims["event"])
        print(model[count].ljust(15),scenario[count].ljust(10),str(int(ptile[count]*100)).zfill(2),nevent[count])
        count = count + 1
# Plot


##########################################################################################
# NO CHANGES BELOW
##########################################################################################
