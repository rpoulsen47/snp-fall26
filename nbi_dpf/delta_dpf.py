"""
delta_dpf.py
Script to calculate the change in the date of peak fall foliage (∆DPF), ignoring no-data values, at each pixel.

Author....Ryan Poulsen
Created...11/17/2026
Updated...11/17/2026

Made with <3.
"""

import rioxarray as rxr
import glob
import os
import numpy as np
from scipy import stats

data_src = "/Volumes/hurricane/snp-fall26/output/dpf/" # Source rasters to stack
data_out = "/Volumes/hurricane/snp-fall26/output/dpf/delta_dpf.tif" # Output location for avg

rasters = sorted(glob.glob(os.path.join(r'F:', data_src, f'*sub*.tif'), recursive=True)) # Get all paths to files in data_src

rsts = [] # empty list to house the stack
for r in rasters: # open and stack files
    rio_r = rxr.open_rasterio(r, masked=True).squeeze("band", drop=True)
    rsts.append(rio_r)

delta_dpf = rsts[0].copy(deep=True) # create a copy of the first raster in the stack (rsts) to use as a template for delta_dpf

for y in range(rsts[0].shape[0]):
    for x in range(rsts[0].shape[1]):
        pixel_timeseries = [] # list to serve as the timeseries for the pixel
        for r in range(len(rsts)):
            pixel_val = rsts[r][y][x]
            if pixel_val != -999: # only append value to pixel_timeseries if the value is good (not no data -999) !!! Will this cause problems later? Going to ignore this for now.... but need to return to this. Maybe will not be a problem when no-data is resolved.
                pixel_timeseries.append(pixel_val)
        lin = stats.linregress(x=[x for x in range(len(pixel_timeseries))], y=pixel_timeseries) # run linear regression
        delta_dpf[y, x] = (lin.slope * len(pixel_timeseries) + lin.intercept) - lin.intercept # use the parameters from the linear regression to calculate ∆DPF for each pixel
    print(f"Row {y + 1} complete.") # announce when a row is completed

delta_dpf.rio.to_raster(data_out) # export delta_dpf to the specified data_out location