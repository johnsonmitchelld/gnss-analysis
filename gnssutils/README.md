# GnssUtils Documentation

The most useful component of this gnssutils package is the EphemerisManager class. This module downloads GNSS ephemeris data from NASA and the German Federal Agency for Cartography and Geodesy (abbreviated BKG) and formats it into Pandas dataframes. 

## Quick Tutorial

To use the EphemerisManager class, initialize an instance, then use the `get_ephemeris(timestamp, satellites)` method to request the most recent observed ephemeris data before a given timestamp. Below is a minimal example.

```python
import datetime
manager = EphemerisManager()
target_time = datetime.datetime(2021, 1, 9, 12, 0, 0, tzinfo=timezone.utc)
data = manager.get_ephemeris(target_time, ['G01', 'G03'])
```

The constructor for the EphemerisManager class accepts an optional data_directory argument. If this directory is not provided, files are cached in the directory `<working_directory>/data`. If that directory does not exist it is created automatically upon the initialization of the EphemerisManager object.

## Background

The [International GNSS Service](https://igs.org/mgex/data-products/#data) maintains an array of GNSS data products available to the public through NASA's Crustal Dynamics Data Information System, the German Bundesamt für Kartographie und Geodäsie (BKG), and the French Institut Géographique National (IGN). The EphemerisManager class relies on [NASA](https://cddis.nasa.gov/Data_and_Derived_Products/GNSS/broadcast_ephemeris_data.html) and [BKG](https://igs.bkg.bund.de/dataandproducts/overviewindex) data.

These organizations provide a wide variety of data offerings, but this project only makes use of the merged broadcast ephemeris files. These are collections of broadcast navigation data received by IGS sites around the world. NASA and BKG both provide GPS and GLONASS-specific files in the Rinex 2.0 format as well as combined files with data from all GNSS systems (Galileo and Beidou included) in Rinex 3.0 format.

* The BKG daily folder and combined file appear at around 00:18 UTC
* NASA GPS and GLONASS files appear around 01:10 UTC
* NASA's combined file from the previous day is updated with ionosphere and leapseconds around 02:00 UTC the following day

looks like optimal strategy is:

```
if data is from yesterday (UTC) or earlier:
    if all you need is GPS and GLONASS:
        get GPS and GLONASS files from NASA for that day
    else:
        try combined BRDC from nasa
        if NASA combined BRDC doesn't exist (most likely because it's from too long ago):
            get gps file from NASA (and GLONASS if necessary)
        if NASA combined BRDC doesn't have leap second and iono data (aka hasn't been post-processed yet):
            get gps file from NASA and combine with NASA combined
if from today UTC:
    get gps file from NASA for ionosphere and leap seconds and combined brdc file from bkg for other sat systems
    if too recent, get those same files from yesterday
```



