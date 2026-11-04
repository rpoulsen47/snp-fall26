"""
ddpf.py
HILARIOUS ATTEMPT TO CULMINATE YEARS OF WORK.

Author....Ryan Poulsen
Created...10/27/2026
Updated...11/03/2026

Made with <3, patagonia time forever.
"""

# raster
import xarray as xr
import numpy as np

# scipy
from scipy import interpolate, optimize, signal

# visualization
import matplotlib.pyplot as plt

# import functions from scripts
import interpolation as interp
import index

# # Load data, calculate NDVI
# years = [year for year in range(2000,2026)] # list of all years
# data_src = "/Volumes/hurricane/snp-fall26/data/modis/mcd43a4_061/" # Raw modis data source

# band1 = interp.temporal_stack(data_src=data_src, year=years[4], band=1) # Load Band1 files and stack by time dimension
# band2 = interp.temporal_stack(data_src=data_src, year=years[4], band=2) # Load Band2 files and stack by time dimension

# ndvi_rs = index.ndvi(band1, band2) # Calculate ndvi

# # interp.export_data(ndvi_rs, "/Volumes/hurricane/snp-fall26/data/modis/ndvi/", "ndvi") # Export ndvi data to .tif files

# # Interpolate NDVI data
# start, end = 186, 365 # Start and end indexes (middle of year, end of year)

# ndvi_rs_int = interp.temporal_interpolation(ndvi_rs)
# interp.export_data(ndvi_rs_int, "/Volumes/hurricane/snp-fall26/data/modis/ndvi_interp/", "ndvi_interp") # Export ndvi data to .tif files

# Smooth NDVI Values
ndvi_rs_int = interp.temporal_stack(data_src="/Volumes/hurricane/snp-fall26/data/modis/ndvi_interp/") # Load Band1 files and stack by time dimension

def smooth_autumn_ndvi_rs(ndvi, start = 186) -> list[xr.DataArray]:
    """
    Creates three DataArrays for the maxNDVI, the minNDVI, and baseNDVI of each pixel in the raster for one year's autumn season.
    ### Parameters
    * **ndvi**: `DataArray`
        * Input ndvi data for a specific autumn season.
    ### Returns
    * `list[DataArray]`
        * New interpolated raster.
    """
    print(ndvi)
    ndvi_smoothed = xr.DataArray(signal.savgol_filter(ndvi, 32, 0))
    autumn_ndvi_smoothed = ndvi_smoothed[start:len(ndvi_smoothed)-1]
    # assign each image in the stack its original DOY
    return autumn_ndvi_smoothed

autumn_ndvi_smoothed = smooth_autumn_ndvi_rs(ndvi_rs_int)

# # Calculate NBI
# def get_nbi_input_params(autumn_ndvi: list[xr.DataArray]) -> tuple[xr.DataArray]:
#     """
#     Creates three DataArrays for the maxNDVI, the minNDVI, and baseNDVI of each pixel in the raster for one year's autumn season.
#     ### Parameters
#     * **ndvi**: `DataArray`
#         * Input ndvi data for a specific autumn season.
#     ### Returns
#     * `list[DataArray]`
#         * New interpolated raster.
#     """
#     maxNDVI_rs = autumn_ndvi[0].copy(True)
#     minNDVI_rs = autumn_ndvi[0].copy(True)

#     for y in range(0, len(autumn_ndvi.dim_1)-1):
#         if y > 2:
#             baseNDVI_rs = maxNDVI_rs - minNDVI_rs
#             return (maxNDVI_rs, minNDVI_rs, baseNDVI_rs)
#         for x in range(0, len(autumn_ndvi.dim_2)-1):
#             doy_vals = []
#             for doy in range(0, len(autumn_ndvi.dim_0)-1):
#                 doy_vals.append(autumn_ndvi[doy][y][x])
#             maxNDVI_rs[y][x] = max(doy_vals)
#             minNDVI_rs[y][x] = min(doy_vals)
            
#     baseNDVI_rs = maxNDVI_rs - minNDVI_rs

#     return (maxNDVI_rs, minNDVI_rs, baseNDVI_rs)

def nbi_xr(autumn_ndvi: list[xr.DataArray]) -> tuple[xr.DataArray]:
    """
    Creates three DataArrays for the maxNDVI, the minNDVI, and baseNDVI of each pixel in the raster for one year's autumn season.
    ### Parameters
    * **ndvi**: `DataArray`
        * Input ndvi data for a specific autumn season.
    ### Returns
    * `list[DataArray]`
        * New interpolated raster.
    * `list[DataArray]`
        * New interpolated raster.
    """
    nbi_rs = autumn_ndvi[0].copy(True)
    peak_date_rs = autumn_ndvi[0].copy(True)

    for y in range(0, len(autumn_ndvi.dim_1)-1):
        for x in range(0, len(autumn_ndvi.dim_2)-1):
            doy_vals = []
            for doy in range(0, len(autumn_ndvi.dim_0)-1):
                doy_vals.append(autumn_ndvi[doy][y][x])

            maxNDVI = max(doy_vals) # Calculate Input Params
            minNDVI = min(doy_vals) # Calculate Input Params
            baseNDVI = maxNDVI - minNDVI # Calculate Input Params
            pIn = [baseNDVI, 0.5, baseNDVI, minNDVI] # Initial guess at the parameters to feed into optimize
            autumn_doy = np.array([i for i in range(len(autumn_ndvi_smoothed.dim_0)-1)]) + 186

            param, covariance = optimize.curve_fit(f=index.logistic_fall, xdata=autumn_doy, ydata=doy_vals, p0=pIn, sigma=1, maxfev=5000) # Find the logistic fall equation that fits the NDVI data, Parameters of the logistic fall curve from optimize.curve_fit and covariance
            print(param)

            # Normalized Brownness Index
            paramA = param[0]
            paramB = param[1]

            nbi_autumn = index.nbi(x=autumn_doy, pA=paramA, pB=paramB) # Calculate NBI using the leaf development parameters from the Logistic Fall Function
            nbi_rs[y][x] = nbi_autumn[np.where(nbi_autumn >= 0.6)[0][0]]
            peak_date_rs[y][x] = autumn_doy[np.where(nbi_autumn >= 0.6)[0][0]]

    return nbi_rs, peak_date_rs

# print(nbi_xr(autumn_ndvi_smoothed)[1][0][0])


# autumn_doy = [i for i in range(len(autumn_ndvi_smoothed)-1)]

# pIn = [basendvi, 0.5, basendvi, minndvi]
# param, covariance = optimize.curve_fit(f=interp.logistic_fall, xdata=autumn_doy, ydata=autumn_ndvi_smoothed, p0=pIn, sigma=1) # Find the logistic fall equation that fits the NDVI data
# print(param) # Parameters of the logistic fall curve from optimize.curve_fit

# pIn = [basendvi[0][0], 0.5, basendvi[0][0], minndvi[0][0]]
# param, covariance = optimize.curve_fit(f=interp.logistic_fall, xdata=[i for i in range(len(autumn_ndvi_smoothed))], ydata=autumn_ndvi_smoothed, p0=pIn, sigma=1) # Find the logistic fall equation that fits the NDVI data
# print(param) # Parameters of the logistic fall curve from optimize.curve_fit


# pIn = [baseNDVI, 0.5, baseNDVI, minNDVI] # Initial guess at the parameters to feed into optimize NEED TO REVIEW THIS WITH SPERA... I deviated from Zhang 2011 and Spera 2023 a little bit