%Script to play around with some of the data while I'm sorting things out


datadir='/Projects/HydroMet/dswales/CMIP6/IVT/';
fileIN=[datadir 'ACCESS-ESM1-5_IVT_IWV_historical.nc'];
temp=double(ncread(fileIN,'IVT'));
%Permute to make dims go time, lat, lon
temp=permute(temp, [3 2 1]);
pcolor(squeeze(temp(1,:,:)))
%Looks like the missing values in ncview were just it trying to overlay a coastline



