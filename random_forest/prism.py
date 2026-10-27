"""
prism.py
HILARIOUS ATTEMPT TO WORK WITH AN UNGODLY AMOUNT OF DATA.
The goal of this program is to take 80GB of climate data,
and turn it into 5 individual rasters.

Author....Ryan Poulsen
Created...10/05/2026
Updated...10/08/2026

Made with <3, fueled by french-press coffee.
"""

from zipfile import ZipFile
import os
import glob

import geopandas as gpd
import matplotlib.pyplot as plt
import rioxarray as rxr
import xarray as xr

def prism_unzipper(pths: list) -> None:
    """
    Unzips a bunch of PRISM climate data.
    ### Parameters
    * **pths**: `list`
        * List of paths (type `str`) to the data
    """
    for pth in pths:
        ziplist = glob.glob(os.path.join(r'F:', pth, '**/*.zip'), recursive=True)
        for file in ziplist:
            subdir = file.split("/")[-1][:21]
            with ZipFile(file) as zObject:
                for i in zObject.filelist:
                    if i.filename.split(".")[-1] == "tif": # Check if tif file; if tif, then extract
                        zObject.extract(i, f"{pth}/{subdir}") # Extract all monthly tifs to a year folder
            zObject.close()

def prism_clipper(aoi, pth):
    """
    Clips the PRISM data to the desired AOI.
    ### Parameters
    * **aoi**: 
        * Area of Interest shapefile (geopandas)
    * **pth**: 
        * Directory with the files to be clipped
    """
    rstlst = glob.glob(f"{pth}/*.tif")
    for file in rstlst:
        rst = rxr.open_rasterio(file)
        rst_rprj = rst.rio.reproject(aoi.crs)
        rst_rprj_clp = rst_rprj.rio.clip_box(aoi.bounds["minx"], aoi.bounds["miny"], aoi.bounds["maxx"], aoi.bounds["maxy"])
        rst_rprj_clp.rio.to_raster(f"{file[:-4]}_snp.tif")


def prism_seasonal(pth):
    """
    Creates seasonal rasters for the PRISM data (Spring Summer Fall)
    3 rasters per year ()
    """
    szns = [["03", "04", "05"], ["06", "07", "08"], ["09", "10", "11"]]
    szn_nms = ["MAM", "JJA", "SON"]

    szn_rsts = []
    for szn in szns:
        rsts = []
        for month in szn:
            rst = rxr.open_rasterio(glob.glob(f"/Volumes/hurricane/snp-fall26/data/predictors/prism/ppt/prism_ppt_us_30s_2000/*{month}_*np.tif")[0])
            rsts.append(rst)
        szn_rst = (rsts[0] + rsts[1] + rsts[2])/3
        szn_rsts.append(szn_rst)

    for rst, nm in zip(szn_rsts, szn_nms):
        rst.rio.to_raster(f"{pth}/{nm}.tif")
        pass


def prism_change():
    """
    Calculates the change over a set amount of time for the seasons and annually
    Results in 5 rasters
    """
    pass

pths = [r"/Volumes/hurricane/snp-fall26/data/predictors/prism/ppt"]
aoi = gpd.read_file("data/snp.gpkg")
pth = r"/Volumes/hurricane/snp-fall26/data/predictors/prism/ppt/prism_ppt_us_30s_2000"
szns = [["03", "04", "05"], ["06", "07", "08"], ["09", "10", "11"]]
prism_clipper(aoi, pth)
# prism_unzipper(pths)


# References
# https://www.geeksforgeeks.org/python/list-all-files-of-certain-type-in-a-directory-using-python/
# https://www.geeksforgeeks.org/python/unzipping-files-in-python/