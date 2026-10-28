"""
ddpf.py
HILARIOUS ATTEMPT TO CULMINATE YEARS OF WORK.

Author....Ryan Poulsen
Created...10/27/2026
Updated...10/28/2026

Made with <3, patagonia time forever.
"""
#****** IMPORTS
# data
import pandas as pd
import numpy as np

# raster
import xarray as xr
import rioxarray as rxr

# file management
import os
import glob

# scipy
from scipy import interpolate, optimize, signal

# visualization
import matplotlib.pyplot as plt

# import functions from scripts
import interpolation as interp
import index

# Load data, calculate NDVI
years = [year for year in range(2000,2026)] # list of all years
data_src = "/Volumes/hurricane/snp-fall26/data/modis/mcd43a4_061/" # Raw modis data source

band1 = interp.temporal_stack(data_src=data_src, year=years[4], band=1) # Load Band1 files and stack by time dimension
band2 = interp.temporal_stack(data_src=data_src, year=years[4], band=2) # Load Band2 files and stack by time dimension

ndvi_rs = index.ndvi(band1, band2) # Calculate ndvi

# interp.export_data(ndvi_rs, "/Volumes/hurricane/snp-fall26/data/modis/ndvi/", "ndvi") # Export ndvi data to .tif files

# Interpolate data
start, end = 186, 365 # Start and end indexes (middle of year, end of year)

ndvi_rs_int = interp.temporal_interpolation(ndvi_rs)
interp.export_data(ndvi_rs_int, "/Volumes/hurricane/snp-fall26/data/modis/ndvi_interp/", "ndvi_interp") # Export ndvi data to .tif files
