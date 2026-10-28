# snp-fall26
## Project Overview
<a href="https://richmond.edu/"><img src="logos/ur.png" align="right" height="138" alt="University of Richmond Website" /></a>
<a href="https://geography.richmond.edu/"><img src="logos/leif.png" align="right" height="138" alt="UR Geography Website" /></a>
This repository is part of the Fall Foliage, Climate Change, and Recreational Tourism research in the University of Richmond's Department of Geography, Environment, and Sustainability. This research focuses on understanding and disentangling the effects of climate change on the timing of fall foliage in National Parks, while considering the impacts on recreational tourism.

This repository contains the code for the senior capstone project "Evaluating Long-Term Temporal Shifts in Foliage Senescence in Response to a Changing Climate in Shenandoah National Park, Virginia". The objective of this project is to understand how the timing of peak fall coloration across Shenandoah National Park is changing from 2000-2025, as a result of a changing climate.

## Data

This project relies on MODIS data (*MOD*erate resolution *I*maging *S*pectroradiometer), specifically the 500 m resolution MODIS MC43A4 Version 6 Nadir BRDF ([MCD43A4.061](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD43A4)) product.

## References

Spera, S. A., Spangler, K. R., Hubert, M. O., & Gorman, M. G. (2023). The effects of climate change on the timing of peak fall foliage in Acadia National Park. *Landscape Ecology, 38(9)*, 2339–2355. <https://doi.org/10.1007/s10980-023-01703-0>

Zhang, X., & Goldberg, M. D. (2011). Monitoring fall foliage coloration dynamics using time-series satellite data. *Remote Sensing of Environment, 115(2)*, 382–391. <https://doi.org/10.1016/j.rse.2010.09.009>

- - -

# Documentation
## `interpolation.temporal_stack()`
Reads in MODIS data from a directory, then creates a new `DataArray` on the dimension *doy* (day of year).
### Parameter
* **data_src**: `str`
    * Path to the directory with the data.
### Return
* `DataArray`
    * The new `DataArray` stacked by *doy*.

## `interpolation.temporal_interpolation()`
Temporally interpolates raster data by the *doy* dimension. Iterates through the raster pixel-by-pixel.
### Parameter
* **rs**: `DataArray`
    * The input raster dataset to be temporally interpolated.
### Return
* `DataArray`
    * New interpolated raster

## `interpolation.ndvi()`
Calculates the Normalized Difference Vegetation Index given red and nir bands.
### Parameters
* **red**: `DataArray`
* **nir**: `DataArray`
### Return
* `DataArray`
    * Normalized Difference Vegetation Index

## `interpolation.smooth_ndvi()`
Uses a Savitzky-Golay smoothing filter to smooth the ndvi data.
### Parameters
* **ndvi**: `array`
    * The ndvi sequence to smooth.
* **window_width**: `int`
    * Integer specifying the number of data points to smooth.
    * A window_width produces a smoother result at the expense of flattening sharp peaks.
    * Default is 32.
* **order**: `int`
    * An integer specifying the order of the derivative desired.
    * Default for smoothing is order 0.
### Return
* `array`
    * The smoothed ndvi data.

## `interpolation.nbi()`
Calculates the Temporally-Normalized Brownness Index (NBI) for a pixel. Based on methodology from Zhang & Goldberg, 2011
### Parameters
* **x**: `array`
    * The doys
* **pA**: `DataArray`
    * Leaf development parameter a (from logistic_fall)
* **pB**: `DataArray`
    * Leaf development parameter b (from logistic_fall)
### Return
* `DataArray`
    * Normalized Brownnness Index
