"""
average_dpf.py
Script to calculate the average date of peak fall foliage, ignoring no-data values.

Author....Ryan Poulsen
Created...11/16/2026
Updated...11/17/2026

Made with <3.
"""

import rioxarray as rxr
import glob
import os

data_src = "/Volumes/hurricane/snp-fall26/output/dpf/" # Source rasters to stack
data_out = "/Volumes/hurricane/snp-fall26/output/dpf/avg_dpf.tif" # Output location for avg

rasters = sorted(glob.glob(os.path.join(r'F:', data_src, f'*sub*.tif'), recursive=True)) # Get all paths to files in data_src

rsts = [] # empty list to house the stack
for r in rasters: # open and stack files
    rio_r = rxr.open_rasterio(r, masked=True).squeeze("band", drop=True)
    rsts.append(rio_r)

avg_dpf = rsts[0].copy(deep=True) # create a copy of the first raster in the stack (rsts) to use as a template for avg_dpf

for y in range(rsts[0].shape[0]):
    for x in range(rsts[0].shape[1]):
        pixel_total = 0 # sum of values across all years at pixel x, y
        value_count = 0 # count of the valid values added to pixel_total
        for r in range(len(rsts)):
            pixel_val = rsts[r][y][x]
            if pixel_val != -999: # only add to pixel_total and value_count if the value is good (not no data -999)
                pixel_total += pixel_val
                value_count += 1
        avg_dpf[y, x] = pixel_total / value_count # set pixel value of avg_dpf[x, y] to the average pixel value
    print(f"Row {y + 1} complete.") # announce when a row is completed

avg_dpf.rio.to_raster(data_out) # export avg_dpf to the specified data_out location