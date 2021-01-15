# gnss-analysis

This repository is a collection of Python notebooks and utility modules for processing GNSS data. The primary source of this data is raw GNSS measurements from Android phones, but the utilities and positioning algorithms should be applicable to measurements from other sources as well.

## notebooks

Example notebooks for GNSS data processing.

## gnssutils

A Python package of utilities for working with GNSS data. The main module is ephemeris_manager, which dowloads and formats the necessary GNSS ephemeris data from NASA or BKG into a Pandas dataframe. See the README in the gnssutils directory for more info.

## data

Cache for data files associated with this project. The repository provides one sample Android GNSS log collected in Seattle.
