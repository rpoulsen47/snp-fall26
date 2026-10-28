"""
index.py
Script of index functions; NDVI & NBI.

Author....Ryan Poulsen
Created...10/28/2026
Updated...10/28/2026

Made with <3, patagonia time forever.
"""

# raster
import xarray as xr
import rioxarray as rxr

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