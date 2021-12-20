##########################################################################################
# Dependencies
##########################################################################################
import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

showPlot = False
verbose  = True

# Which future scenario(s) to plot?
scn_req = ["ssp126","ssp245","ssp370","ssp585"]

# Where are the slab files?
dirIN = "/Projects/HydroMet/dswales/CMIP6/slabs/slabtest1/"

# Where to store plots?
caseID = 'slabtest1'
dirOUT = "/Projects/HydroMet/dswales/CMIP6/slabs/"+caseID+"/"

# Axis range for plots
xrange = [0,500]

# Increase to remove number of points in PDFs
slab_stride = 2

##########################################################################################
# NO CHANGES BELOW
##########################################################################################

# Get model(s) and cooresponding forcing scenario information.
file_list = []
modelname = []
scenario  = []
for files in os.listdir(dirIN):
    if files.endswith(".nc"):
        file_list.append(files)
        modelname.append(str(files)[0:files.find('_IVT')])
        scenario.append(str(files)[files.find('IWV_')+4:files.find('.nc')])

# How many models are there?        
unique_modelname = []
for model in modelname:
    if model not in unique_modelname:
        unique_modelname.append(model)

# Which models have future scenarios?
models_w_future    = []
models_w_histonly  = []
for model in unique_modelname:
    fi = np.where(model == np.array([modelname],dtype='str'))[1]
    if (len(fi) > 1):
        models_w_future.append(model)
    else:
        models_w_histonly.append(model)
if verbose: print(models_w_future)
if verbose: print(models_w_histonly)

if verbose: print("-------------------------------------------------------------")
if verbose: print("Number of total models:  ",len(modelname))
if verbose: print("          unique models: ",len(unique_modelname))
if verbose: print("Models with future scenarios available: ",str(len(models_w_future)))
for model in models_w_future:
    if verbose: print("   ",model)
    ims = np.where(model == np.array([modelname],dtype='str'))[1]
    for iscn in ims:
        if verbose: print("       ",scenario[iscn])
if verbose: print("Models with only historical available:  ",str(len(models_w_histonly)))
for model in models_w_histonly:
    if verbose: print("   ",model)
if verbose: print("-------------------------------------------------------------")


if(not os.path.isdir(dirOUT+"plots/")): os.mkdir(dirOUT+"plots/")

##########################################################################################
# Make plots for models with future experiments
##########################################################################################
for model in models_w_future:
    for scn in scn_req:
        mi_f  = np.where((model == np.array([modelname],dtype='str')) & (scn == np.array([scenario],dtype='str')))[1]
        mi_h  = np.where((model == np.array([modelname],dtype='str')) & ("historical" == np.array([scenario],dtype='str')))[1]

        plotOUT = dirOUT+"plots/pdf.historical."+scn+"."+modelname[mi_h[0]]+".png"
        # Historical
        data_h = xr.open_dataset(dirIN+file_list[mi_h[0]])
        pdf_h  = data_h.PDF.values
        bins_h = data_h.bin.values
        npts_h = len(data_h.slab.values)

        # Future
        data_f = xr.open_dataset(dirIN+file_list[mi_f[0]])
        pdf_f  = data_f.PDF.values
        bins_f = data_f.bin.values
        npts_f = len(data_f.slab.values)

        print("PDF plot: ",plotOUT)
        fig=plt.figure(figsize=(8, 6))
        #
        plt.subplot(3, 1, 1)
        for slab in range(0,npts_h,slab_stride):
            plt.plot(bins_h, 100.*pdf_h[int(slab),:]/np.sum(pdf_h[int(slab),:]))
        plt.xlabel("IVT (kg/m/s)")
        plt.ylabel("Frequency (%)")
        plt.ylim([0,8])
        plt.xlim(xrange)
        #
        plt.subplot(3, 1, 2)
        for slab in range(0,npts_f,slab_stride):
            plt.plot(bins_f, 100.*pdf_f[int(slab),:]/np.sum(pdf_f[int(slab),:]))
        plt.xlabel("IVT (kg/m/s)")
        plt.ylabel("Frequency (%)")
        plt.ylim([0,8])
        plt.xlim(xrange)
        #
        plt.subplot(3, 1, 3)
        plt.plot([0,1e5],[0,0])
        for slab in range(0,npts_h,slab_stride):
            plt.plot(bins_h, 100.*((pdf_f[int(slab),:]/np.sum(pdf_f[int(slab),:])) - \
                                   (pdf_h[int(slab),:]/np.sum(pdf_h[int(slab),:]))))
        plt.xlabel("IVT (kg/m/s)")
        plt.ylabel("Frequency (%)")
        plt.ylim([-2,2])
        plt.xlim(xrange)
        #
        plt.savefig(plotOUT)
        if (showPlot): plt.show()
        plt.close(fig)

##########################################################################################
# Make plots for models with only historical
##########################################################################################
for model in models_w_histonly:
    mi     = np.where(model == np.array([modelname],dtype='str'))[1]
    data   = xr.open_dataset(dirIN+file_list[mi[0]])
    pdf    = data.PDF.values
    bins   = data.bin.values
    npts_h = len(data.slab.values)

    plotOUT = dirOUT+"plots/pdf.historical."+modelname[mi[0]]+".png"
    print("PDF plot: ",plotOUT)
    fig=plt.figure(figsize=(8, 6))
    plt.gca().set_prop_cycle(plt.cycler('color', plt.cm.jet(np.linspace(0, 1, npts_h))))
    for slab in range(0,npts_h,slab_stride):
        plt.plot(bins, 100.*pdf[int(slab),:]/np.sum(pdf[int(slab),:]))
    plt.xlabel("IVT (kg/m/s)")
    plt.ylabel("Frequency (%)")
    plt.ylim([0,8])
    plt.savefig(plotOUT)
    if (showPlot): plt.show()
    plt.close(fig)
