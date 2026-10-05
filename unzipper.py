"""
unzipper.py
HILARIOUS ATTEMPT TO WORK WITH AN UNGODLY AMOUNT OF DATA.
Script to unzip all files within a directory.

Author....Ryan Poulsen
Created...10/05/2026
Updated...10/05/2026

Made with <3
"""

from zipfile import ZipFile
import os
import glob

pth = r"/Volumes/hurricane/snp-fall26/data/predictors/prism/ppt/2000"

# Extract all files from zip files in the prism folder
# Ideally keep the files together in their respective directories
for file in glob.glob(os.path.join(r'F:', pth, '**/*.zip'), recursive=True):
    with ZipFile(file) as zObject:
        for i in zObject.filelist:
            print(i.filename)
        # zObject.extractall(path=pth)
    zObject.close()


# References
# https://www.geeksforgeeks.org/python/list-all-files-of-certain-type-in-a-directory-using-python/
# https://www.geeksforgeeks.org/python/unzipping-files-in-python/