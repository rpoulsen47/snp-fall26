"""
dpc.py
HILARIOUS ATTEMPT TO CULMINATE YEARS OF WORK.
Main file to calculate the date of peak coloration.

Author....Ryan Poulsen
Created...10/27/2026
Updated...11/16/2026

Made with <3, and remember, this is for the leaves.
"""

import interpolation as interp
import index

import rioxarray as rxr
import geopandas as gpd

# Set year range, load data
years = [year for year in range(2000, 2021)] # list of all years
data_src = "/Volumes/hurricane/snp-fall26/data/modis/mcd43a4_061/" # Raw modis data source
# ndvi_src = "/Volumes/hurricane/snp-fall26/output/ndvi/"
# aoi = gpd.read_file("/Volumes/hurricane/snp-fall26/shen-sample-request.geojson") # AOI bounds from GeoJSON (optional for subsetting the data, useful for testing)x

for year in years: # run the following code for each year in the study period

    band1 = interp.stack_on_doy(data_src=data_src, year=year, band=1) # Load Band1 files and stack by time dimension
    band2 = interp.stack_on_doy(data_src=data_src, year=year, band=2) # Load Band2 files and stack by time dimension

    ndvi_rs = index.ndvi(band2, band1) # Calculate ndvi

    # ndvi_rs = ndvi_rs.rio.clip(aoi.geometry, aoi.crs) # Clip to subset AOI

    # Interpolate NDVI data
    ndvi_rs_int = interp.temporally_weighted_interpolation(ndvi_rs)
    interp.export_doy_stack(ndvi_rs_int, f"/Volumes/hurricane/snp-fall26/output/ndvi/", "ndvi_interpolated_subset") # Export ndvi data to .tif files

    # ndvi_rs_int = interp.stack_on_doy(data_src=ndvi_src, year=year)

    # Smooth Autumn NDVI Values
    autumn_ndvi_smoothed = index.smooth_senescent_ndvi(ndvi_rs_int)

    # Calculate NBI
    nbi_rs, peak_date_rs = index.nbi(autumn_ndvi_smoothed)

    peak_date_rs.rio.to_raster(f"/Volumes/hurricane/snp-fall26/output/dpf/dpf_{year}.tif")
    nbi_rs.rio.to_raster(f"/Volumes/hurricane/snp-fall26/output/nbi/nbi_{year}.tif")