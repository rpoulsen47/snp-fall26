"""
interpolation.py
HILARIOUS ATTEMPT TO MAKE THIS A GIANT PROGRAM

Author....Ryan Poulsen
Created...11/04/2025
Updated...11/02/2026

Made with <3, fueled by mint tea and chocolate chips.
"""

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

# Raster Functions
def temporal_stack(data_src: str, year: int, band: int) -> xr.DataArray:
    """
    Reads in MODIS data from a directory, then creates a new `DataArray` on the dimension *doy*.
    ### Parameters
    * **data_src**: `str`
        * Path to the directory with the data.
    ### Returns
    * `DataArray`
        * The new `DataArray` stacked by *doy*.
    """
    rasters = sorted(glob.glob(os.path.join(r'F:', data_src, f'*Band{band}*doy{year}*.tif'), recursive=True)) # Get all paths to files in data_src
    crs_src = rxr.open_rasterio(rasters[0], masked=True).squeeze("band", drop=True).rio.crs # Get the crs of the first raster in the directory to use as template for the others to ensure all rasters match.

    rsts, doys = [], [] # blank lists for rasters and doys
    year = None # empty variable for the year
    for r in rasters: # for each raster, open it, get the date, reproject it, then add the raster and the doy to the rsts and doys lists respectively
        rio_r = rxr.open_rasterio(r, masked=True).squeeze("band", drop=True)
        year, doy = get_date(r) # get the year and the doy with the get_date() function (uses filename)
        rio_r.rio.reproject(crs_src) # Might not be necessary, but is probably good practice to ensure that all rasters are in the same crs
        rsts.append(rio_r)
        doys.append(doy)

    data = xr.Dataset({d: r for d, r in zip(doys, rsts)}).to_array(dim="doy") # Creates a new DataArray with each band stacked.
    data.attrs.update({"year":year}) # add the year as an attribute
    return data

def temporal_stack(data_src: str) -> xr.DataArray:
    """
    Reads in MODIS data from a directory, then creates a new `DataArray` on the dimension *doy*.
    ### Parameters
    * **data_src**: `str`
        * Path to the directory with the data.
    ### Returns
    * `DataArray`
        * The new `DataArray` stacked by *doy*.
    """
    rasters = sorted(glob.glob(os.path.join(r'F:', data_src, f'*.tif'), recursive=True)) # Get all paths to files in data_src
    crs_src = rxr.open_rasterio(rasters[0], masked=True).squeeze("band", drop=True).rio.crs # Get the crs of the first raster in the directory to use as template for the others to ensure all rasters match.

    rsts, doys = [], [] # blank lists for rasters and doys
    year = None # empty variable for the year
    for r in rasters: # for each raster, open it, get the date, reproject it, then add the raster and the doy to the rsts and doys lists respectively
        rio_r = rxr.open_rasterio(r, masked=True).squeeze("band", drop=True)
        year, doy = get_date(r) # get the year and the doy with the get_date() function (uses filename)
        rio_r.rio.reproject(crs_src) # Might not be necessary, but is probably good practice to ensure that all rasters are in the same crs
        rsts.append(rio_r)
        doys.append(doy)

    data = xr.Dataset({d: r for d, r in zip(doys, rsts)}).to_array(dim="doy") # Creates a new DataArray with each band stacked.
    data.attrs.update({"year":year}) # add the year as an attribute
    return data


def get_date(path: str) -> tuple:
    """
    Gets information about the date of a raster from filepath. ("doyYEARDOY" must be present in filepath)
    ### Parameters
    * **path**: `str`
    ### Returns
    * `tuple`
        * two ints, year and doy
    """
    index = path.find("doy") + 3
    year = path[index:index+4]
    doy = path[index+4:index+7]
    return int(year), int(doy)

def export_data(rs:xr.DataArray, path:str, prefix:str="rs") -> None:
    """
    Exports a raster to tiff file with the naming convention <prefix>_doyYEARDOY.tif
    ### Parameters
    * **rs**: `DataArray`
        * Raster dataset to be exported.
    * **path**: `str`
        * Output location for the tiff file.
    * **prefix**: `str`
        * Prefix to be appended to the file's name.
    ### Returns
    * `None`
    """
    for r in rs:
        out = f"{os.path.expanduser(path)}/{prefix}_doy{rs.attrs['year']}{int(r.doy):03d}.tif"
        r.rio.to_raster(out)


# Interpolation Functions
def interpolate_pixel(rs: xr.DataArray, x:int, y:int, display:bool=False) -> np.array:
    """
    Exports a raster to tiff file with the naming convention <prefix>_doyYEARDOY.tif
    ### Parameters
    * **rs**: `DataArray`
        * Input raster dataset with the pixel to be interpolated.
    * **y**: `int`
        * y-coordinate of the pixel to be interpolated.
    * **x**: `int`
        * x-coordinate of the pixel to be interpolated.
    * **display**: `bool`, *optional*
        * If `True`, the timeseries of the pixel value will be displayed.
        * `False` by default.
    ### Returns
    * `array`
        * A new array of the interpolated values.
    """

    doys = np.array([i for i in range(int(rs[0].doy), len(rs)+int(rs[0].doy))]) # Get a list of the doys
    start, stop = doys[0], doys[-1]
    values = np.array([rs.sel({'doy':t})[y][x] for t in doys])
    dv = pd.DataFrame({"doy": doys, "value": values}).set_index("doy", drop=True)

    
    dv_nonan = dv.dropna().reset_index()

    values = np.array(dv_nonan["value"])
    doys = np.array(dv_nonan["doy"])

    f = interpolate.interp1d(doys, values, fill_value="extrapolate")
    doy_new = np.linspace(start=start, stop=stop, num=stop)
    
    print(f"Pixel at y{y}, x{x} interpolated.")

    if display:
        plt.plot(doy_new, f(doy_new), "--", color="#2679B4", label="Interpolated Values")  #f_cubic(temp_new) tells it to estimate the enzyme activity at all 200 temps
        plt.plot(doys, values, 'o', color="#d06f1e", label="Original Data")
        plt.ylim(0, 1)
        plt.xlabel("Day of Year")
        plt.ylabel("NDVI Value")
        plt.title(f"NDVI Values in {rs.attrs['year']} at x{x}, y{y}")
        plt.legend()
        plt.show()

    return f(doy_new)

def temporal_interpolation(rs:xr.DataArray) -> xr.DataArray:
    """
    Temporally interpolates raster data by the *doy* dimension. Iterates through the raster pixel-by-pixel.\n
    NOTE: This does work, however it takes. so. LONG.
    ### Parameters
    * **rs**: `DataArray`
        * Input raster dataset to be interpolated.
    ### Returns
    * `DataArray`
        * New interpolated raster.
    """
    rs_new = rs.copy() # Create a copy of the original raster to update with interpolated data
    for y in range(rs.shape[1]):
        for x in range(rs.shape[2]):
            new_vals = interpolate_pixel(rs=rs, y=int(y), x=int(x)) # New, interpolated, value for each doy in a pixel
            for ind, val in enumerate(new_vals):
                rs_new.sel({'doy':ind+1})[y][x] = val # Sets the values of the current pixel to be the new_vals.
    return rs_new