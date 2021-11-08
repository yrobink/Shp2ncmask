# Shp2ncmask

Tools to transform a shapefile in a netcdf mask. The grid, input and output
projections can be customized.

## Requires

The script use `python3`, and requires the following libraries:

- numpy
- xarray
- netCDF4
- pyproj
- shapely
- geopandas
- matplotlib

This script has been tested with a miniconda installation on the `conda-forge`
channel, and on the python installation of ubuntu 20.04 LTS.

## Installation and documentation

Start by install with the command:

~~~bash
python3 setup.py install
~~~

and just run the following command to access to the documentation:

~~~bash
shp2ncmask --help
~~~


## Examples

### Metropolitan France in lat/lon projection

~~~bash
data_test=data/gadm36_FRA_shp/gadm36_FRA_0.shp
shp2ncmask -m weight -i $data_test -iepsg 4326 -o data/mask_4326.nc -g -5,10,0.5,41,52,0.5 -oepsg 4326 -fig figures/control_4326.png -fepsg 4326
~~~

![Alt](/figures/control_4326.png)

### Metropolitan France in LambertII projection

~~~bash
data_test=data/gadm36_FRA_shp/gadm36_FRA_0.shp
shp2ncmask -m weight -i $data_test -iepsg 4326 -o data/mask_27572.nc -g 60000,1196000,64000,1617000,2681000,64000 -oepsg 27572 -fig figures/control_27572_64km.png -fepsg 4326
~~~

![Alt](/figures/control_27572_64km.png)

### Ile-de-France region from metropolitan France in lat/lon projection

~~~bash
## We print the columns, rows, select to find bounds and we build the mask.
data_test=data/gadm36_FRA_shp/gadm36_FRA_1.shp
shp2ncmask -i $data_test -lc ## --list--columns
shp2ncmask -i $data_test -dc NAME_1 ## --describe-column
shp2ncmask -i $data_test -s NAME_1 'Île-de-France' -b
shp2ncmask -m weight -i $data_test -s NAME_1 'Île-de-France' -g 1.4,3.6,0.05,48.1,49.3,0.05 -o data/mask_IDF_4326.nc -fig figures/control_IDF_4326.png -fepsg 4326
~~~

![Alt](/figures/control_IDF_4326.png)


### Ile-de-France region from metropolitan France in LambertII projection

~~~bash
## The last is also the IDF, but in LambertII coordinates, so we change the input epsg to find the bounds
data_test=data/gadm36_FRA_shp/gadm36_FRA_1.shp
shp2ncmask -i $data_test -s NAME_1 'Île-de-France' -iepsg 27572 -b
shp2ncmask -m weight -i $data_test -s NAME_1 'Île-de-France' -g 534000,700000,8000,2340000,2480000,8000 -o data/mask_IDF_27572.nc -oepsg 27572 -fig figures/control_IDF_27572_8km.png -fepsg 4326
~~~

![Alt](/figures/control_IDF_27572_8km.png)


## License

Copyright(c) 2021 Yoann Robin

This file is part of Shp2ncmask.

Shp2ncmask is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Shp2ncmask is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Shp2ncmask.  If not, see <https://www.gnu.org/licenses/>.

