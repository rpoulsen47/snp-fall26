"""
index.py
Script of vegetation indices; NDVI & NBI

Author....Ryan Poulsen
Created...10/28/2026
Updated...11/02/2026

Made with <3, patagonia time forever.
"""

import numpy as np
import xarray as xr
from scipy import optimize, signal

# NDVI Functions
def ndvi(red: xr.DataArray, nir: xr.DataArray) -> xr.DataArray:
    """
    Calculates the Normalized Difference Vegetation Index given red and nir bands.
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

def smooth_ndvi(ndvi: list, window_width: int = 32, order: int = 0) -> xr.DataArray:
    """
    Uses a Savitzky-Golay smoothing filter to smooth the ndvi data.
    ### Parameters
    * **ndvi**: `array`
        * The ndvi sequence to smooth.
    * **window_width**: `int`
        * Integer specifying the number of data points to smooth.
        * A window_width produces a smoother result at the expense of flattening sharp peaks.
        * Default is 32.
    * **order**: `int`\n
        * An integer specifying the order of the derivative desired.
        * Default for smoothing is order 0.
    ### Returns
    * `array`
        * The smoothed ndvi data.
    """
    return doy_dim(xr.DataArray(signal.savgol_filter(ndvi, window_width, order)))
    # return doy_dim(xr.DataArray(signal.savgol_filter(ndvi, window_width, order)))

def nbi(x, pA, pB, x0: int = 186):
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

# NBI Functions
def logistic_fall(x, a: float, b: float, c: float, d: float, x0 = 186):
    """
    Adapted from Zhang et al., 2011 and Spera et al., 2023\n
    ### Parameters
    * **x**: `array`
        * Doy
    * **x0**: `float`
        * Starting x value; offset.
    * **a**: `float`
        * Leaf development parameter a
    * **b**: `float`
        * Leaf development parameter b
    * **c**: `float`
        * base NDVI value
    * **d**: `float`
        * Minimum NDVI value (c+d = maxNDVI value)
    * **t**: `int`\n
        * Time in days
    ### Returns
    * `array`
        * Sigmoidal function values
    """
    #IT WORKKKEKDD! LET'S FUCKING GOOOOOOOOOOOOOO
    return (c/(1+np.exp(a+b*(x-x0))))+d

def logistic_pixel(ndvi_rs: xr.DataArray, x:int, y:int, start:int=180, end:int=366) -> list:
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

    doys = xr.DataArray([i for i in range(start, end)])
    ndvi_rs_p = xr.DataArray([ndvi_rs.sel({"doy":t})[x][y] for t in range(start, end)])

    maxNDVI = ndvi_rs_p.max()
    minNDVI = ndvi_rs_p.min()
    baseNDVI = maxNDVI - minNDVI

    pIn = [baseNDVI, 0.5, baseNDVI, minNDVI] # Initial guess at the parameters to feed into optimize

    param = optimize.curve_fit(f=logistic_fall, xdata=doys, ydata=ndvi_rs_p, p0=pIn, sigma=1) # Find the logistic fall equation that fits the NDVI data

    return param # Parameters of the logistic fall curve from optimize.curve_fit

def calculate_peak_pixel(ndvi_rs: xr.DataArray, start:int=180, end:int=366):
    """
    Fits the logistic fall function to the autumn ndvi data.\n
    ### Parameters
    * **ndvi_rs**: `xr.DataArray`\n
        * The data to calculate the curve for.
    * **start**: `int`
        * Start doy of fall season, alternatively, provide the doy of the max ndvi value.
        * Default `185`.
    * **end**: `int`
        * End doy. 
        * Default `365`.
    * **display**: `bool`, *optional*
        * Whether or not to display a graph of the senescence curve.
        * Default `False`.
    ### Returns
    * `list`
        * List of the logistic fall equation parameters in order a, b, c, d.
    """
    ndvi_autumn_sm = smooth_ndvi(ndvi_rs) # Smooth the ndvi values using Savisky-Golay filter

    for y in range(ndvi_rs.shape[1]):
        for x in range(ndvi_rs.shape[2]):
            params = logistic_pixel(ndvi_autumn_sm, x, y, start, end)
            print(params)

def doy_dim(rs: xr.DataArray):
    return rs.expand_dims({"doy": [doy for doy in range(1, len(rs)+1)]})