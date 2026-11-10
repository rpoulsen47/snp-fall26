"""
index.py
Script of vegetation indices and their helpers; NDVI & NBI

Author....Ryan Poulsen
Created...10/28/2026
Updated...11/09/2026

Made with <3, patagonia time forever.
"""

import numpy as np
import xarray as xr
from scipy import optimize, signal

# NDVI Functions
def ndvi(nir: xr.DataArray, red: xr.DataArray) -> xr.DataArray:
    """
    Calculates the Normalized Difference Vegetation Index given red and nir bands. (nir - red) / (nir + red)
    ### Parameters
    * **red**: `DataArray`
    * **nir**: `DataArray`
    ### Returns
    * `DataArray`
        * Normalized Difference Vegetation Index
    """
    ndvi = (nir - red) / (nir + red)
    ndvi.attrs.update(red.attrs) 
    return ndvi

def smooth_senescent_ndvi(ndvi) -> xr.DataArray:
    """
    Uses a Savitzky-Golay smoothing filter to smooth the ndvi data for the senescent phase of the NDVI (after day 186, the middle of the calendar year).
    ### Parameters
    * **ndvi**: `array`
        * The ndvi sequence to smooth.
    ### Returns
    * `array`
        * The smoothed ndvi data for the senescent phase.
    """
    ndvi_smoothed = xr.DataArray(signal.savgol_filter(ndvi, 32, 0), coords=ndvi.coords, attrs=ndvi.attrs)
    return ndvi_smoothed[186:len(ndvi_smoothed)-1]

# Logistic Fall Functions
def logistic_fall(x, a: float, b: float, c: float, d: float, x0 = 186):
    """
    Adapted from Zhang et al., 2011 and Spera et al., 2023\n
    ### Parameters
    * **x**: `np.array`
        * Doy
    * **a**: `float`
        * Leaf development parameter a
    * **b**: `float`
        * Leaf development parameter b
    * **c**: `float`
        * base NDVI value
    * **d**: `float`
        * Minimum NDVI value (c+d = maxNDVI value)
    * **x0**: `float`
        * Starting x value; offset. (default 186)
    ### Returns
    * `np.array`
        * Sigmoidal function values
    """
    return (c/(1+np.exp(a+b*(x-x0))))+d

def logistic_fall_pixel(ndvi_rs: xr.DataArray, x:int, y:int, start:int=186) -> list:
    """
    Fits the logistic fall function to the autumn ndvi data.\n
    ### Parameters
    * **ndvi_rs**: `xr.DataArray`\n
        * The data to calculate the curve for.
    * **x**: `int`\n
        * The x coordinate of the pixel
    * **y**: `int`\n
        * The y coordinate of the pixel
    ### Returns
    * `list`
        * List of the logistic fall equation parameters in order a, b, c, d.
    """
    end = start + len(ndvi_rs)
    doys = xr.DataArray([i for i in range(start, end)])
    ndvi_rs_p = xr.DataArray([ndvi_rs.sel({"doy":t})[x][y] for t in range(start, end)])

    maxNDVI = ndvi_rs_p.max()
    minNDVI = ndvi_rs_p.min()
    baseNDVI = maxNDVI - minNDVI

    pIn = [baseNDVI, 0.5, baseNDVI, minNDVI] # Initial guess at the parameters to feed into optimize

    param = optimize.curve_fit(f=logistic_fall, xdata=doys, ydata=ndvi_rs_p, p0=pIn, sigma=1) # Find the logistic fall equation that fits the NDVI data

    return param # Parameters of the logistic fall curve from optimize.curve_fit

# NBI Functions
def nbi(autumn_ndvi: list[xr.DataArray]) -> tuple[xr.DataArray]:
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

    for y in range(0, len(autumn_ndvi.y)):
        for x in range(0, len(autumn_ndvi.x)):
            doy_vals = []
            for doy in range(0, len(autumn_ndvi.doy)-1):
                doy_vals.append(autumn_ndvi[doy][y][x])

            maxNDVI = max(doy_vals) # Calculate Input Params
            minNDVI = min(doy_vals) # Calculate Input Params
            baseNDVI = maxNDVI - minNDVI # Calculate Input Params
            pIn = [baseNDVI, 0.5, baseNDVI, minNDVI] # Initial guess at the parameters to feed into optimize
            autumn_doy = np.array([i for i in range(len(autumn_ndvi.doy)-1)]) + 186

            try:
                param, covariance = optimize.curve_fit(f=logistic_fall, xdata=autumn_doy, ydata=doy_vals, p0=pIn, sigma=1) # Find the logistic fall equation that fits the NDVI data, Parameters of the logistic fall curve from optimize.curve_fit and covariance

                # Normalized Brownness Index
                paramA = param[0]
                paramB = param[1]

                nbi_autumn = nbi_pixel(x=autumn_doy, pA=paramA, pB=paramB) # Calculate NBI using the leaf development parameters from the Logistic Fall Function

                nbi_rs[y][x] = nbi_autumn[np.where(nbi_autumn >= 0.6)[0][0]]
                peak_date_rs[y][x] = autumn_doy[np.where(nbi_autumn >= 0.6)[0][0]]

            except: #RuntimeError or IndexError set to nodata value of -999 (this is because the pixel is likely an urban pixel or evergreen)
                nbi_rs[y][x] = -999
                peak_date_rs[y][x] = -999

            print(f"({int(peak_date_rs[y][x])}, {float(nbi_rs[y][x])}) @ ({x}, {y})")

    return nbi_rs, peak_date_rs

def nbi_pixel(x, pA, pB, x0: int = 186):
    """
    (Zhang et al., 2011)\n
    ### Parameters
    * **x**: `array`\n
        * The doys
    * **pA**: `DataArray`
        * Leaf development parameter a (from logistic_fall)
    * **pB**: `DataArray`
        * Leaf development parameter b (from logistic_fall)
    ### Returns
    * `DataArray`
        * Normalized Difference Brownnness Index
    """
    return 1-1/(1+np.exp(pA+(x-x0)*pB))