"""
unzipper.py
HILARIOUS ATTEMPT TO WORK WITH AN UNGODLY AMOUNT OF DATA.
The goal of this program is to take 80GB of climate data,
and turn it into 5 individual rasters.

Author....Ryan Poulsen
Created...10/05/2026
Updated...10/07/2026

Made with <3, fueled by french-press coffee.
"""

from zipfile import ZipFile
import os
import glob


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

def prism_clipper(aoi):
    """
    Clips the PRISM data to the desired AOI.
    ### Parameters
    * **aoi**: 
        * Area of Interest shapefile
    """
    pass

def prism_seasonal():
    """
    Creates seasonal rasters for the PRISM data
    5 rasters per year ()
    """
    pass

def prism_change():
    """
    Calculates the change over a set amount of time for the seasons and annually
    Results in 5 rasters
    """
    pass

pths = [r"/Volumes/hurricane/snp-fall26/data/predictors/prism/ppt"]
prism_unzipper(pths)


# References
# https://www.geeksforgeeks.org/python/list-all-files-of-certain-type-in-a-directory-using-python/
# https://www.geeksforgeeks.org/python/unzipping-files-in-python/