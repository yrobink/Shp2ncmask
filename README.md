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

This script has been tested with a miniconda installation on the `conda-forge` channel.

## Documentation

### Parameters

`-g` (or `--grid`) [comma separated float]\
&nbsp;&nbsp;&nbsp;&nbsp;Grid used. See the grid section.\
`-i` (or `--input`) [string]\
&nbsp;&nbsp;&nbsp;&nbsp;The input shapefile.\
`-o` (or `--output`) [string]\
&nbsp;&nbsp;&nbsp;&nbsp;The output netcdf file.


### Optional parameters

`--help`\
&nbsp;&nbsp;&nbsp;&nbsp;Print the documentation.\
`-b` (or `--bounds`)\
&nbsp;&nbsp;&nbsp;&nbsp;Print the bounds of input file and quit. Can be used with `'-s'` and `'-iepsg'`.\
`-lc` (or `--list-columns`)\
&nbsp;&nbsp;&nbsp;&nbsp;List the columns of the shapefile and quit.\
`-dc` (or `--describe-column`)\
&nbsp;&nbsp;&nbsp;&nbsp;Describe values of a column.\
`-s` (or `--select`) [string and string]\
&nbsp;&nbsp;&nbsp;&nbsp;Select a row of a column. Must be pass as `'-s COL_NAME ROW_NAME'`\
`-m` (or `--method`) [string] default is 'point'.\
&nbsp;&nbsp;&nbsp;&nbsp;Method used to build the mask. See the method section.\
`--threshold` [float] default is 0.8\
&nbsp;&nbsp;&nbsp;&nbsp;Threshold used by the method 'threshold'.\
`-iepsg` (or `--input-epsg`) [int] default is 4326.\
&nbsp;&nbsp;&nbsp;&nbsp;epsg code of the input shapefile.\
`-oepsg` (or `--output-epsg`) [int] default is 4326.\
&nbsp;&nbsp;&nbsp;&nbsp;epsg code of the output mask.\
`--point-per-edge` [int] default is 100.\
&nbsp;&nbsp;&nbsp;&nbsp;Point per edge, see grid section.\
`-fig` (or `--figure`) [string]\
&nbsp;&nbsp;&nbsp;&nbsp;File of a figure which plot the mask.\
`-fepsg` (or `--figure-epsg`) default is 4326.\
&nbsp;&nbsp;&nbsp;&nbsp;epsg code of the figure.


### About epsg

The EPSG (European Petroleum Survey Group) is a code to identify a cartographic
projection. For example:
- epsg:4326 is the classic latitude / longitude projection (also called WGS 84)
- epsg:27572 is a deprecated Lambert projection, but still widely used to represent metropolitan France. 
- epsg:3395 is the Mercator projection.
- see https://spatialreference.org/ for a list of epsg projections.


### Grid

The grid is represented by 6 comma separated values taking the form:
~~~bash
-g xmin,xmax,dx,ymin,ymax,dy
~~~
where:
- `xmin` is the min value of the x-axis,
- `xmax` is the max value of the x-axis,
- `dx` is the step between xmin and xmax,
- `ymin` is the min value of the y-axis,
- `ymax` is the max value of the y-axis,
- `dy` is the step between xmin and xmax.

Note 1: The first point of the x-axis is `xmin`, but the last point is the
maximal value of the form `'xmin + N * dx'` lower than `'xmax + dx / 2'` (and the
same for the y-axis).

Note 2: To compute the area, cells are re-projected in the Mercator projection.
Thus a cell defined by the four corners is again a cell in the Mercator
projection, but which not represente the area of the original projection. To
overcome this problem, a cell is not defined by only its four corners, but each
edge of each cell is defined by `'--point-per-edge'` points, equally spaced
between the corners. The default value of `'--point-per-edge'` is equal to 100.


### Methods

`'point'`\
&nbsp;&nbsp;&nbsp;&nbsp;Each grid cell is represented by its center. The value is equal to 1 if the center is in the interior of the polygons defined by the shapefile, 0 otherwise.\
`'weight'`\
&nbsp;&nbsp;&nbsp;&nbsp;The value of each grid cell is the percent of area defined by the intersection of the polygons of the shapefile and the cell.\
`'threshold'`\
&nbsp;&nbsp;&nbsp;&nbsp;Start from the 'weight' mask, all values greater than the '--threshold' are replaced by 1, 0 otherwise.\
`'interior'`\
&nbsp;&nbsp;&nbsp;&nbsp;Start from the 'weight' mask, all values lower than 1 are replaced by 0. This correspond to assign 1 only at cells inside the polygons defined by the shapefile.\
`'exterior'`\
&nbsp;&nbsp;&nbsp;&nbsp;Start from the 'weight' mask, all values greater than 0 are replaced by 1. This correspond to assign 0 only at cells outside the polygons defined by the shapefile.

## Shapefile sources

Two (not exhaustive) sources of shapefile are Natural Earth and GADM-3.6:
- [https://www.naturalearthdata.com/](https://www.naturalearthdata.com/)
- [https://gadm.org/download_country_v3.html](https://gadm.org/download_country_v3.html)


## Examples

### Metropolitan France in lat/lon projection

~~~bash
data_test=data/gadm36_FRA_shp/gadm36_FRA_0.shp
./shp2ncmask.py -m weight -i $data_test -iepsg 4326 -o data/mask_4326.nc -g -5,10,0.5,41,52,0.5 -oepsg 4326 -fig figures/control_4326.png -fepsg 4326
~~~

![Alt](/figures/control_4326.png)

### Metropolitan France in LambertII projection

~~~bash
data_test=data/gadm36_FRA_shp/gadm36_FRA_0.shp
./shp2ncmask.py -m weight -i $data_test -iepsg 4326 -o data/mask_27572.nc -g 60000,1196000,64000,1617000,2681000,64000 -oepsg 27572 -fig figures/control_27572_64km.png -fepsg 4326
~~~

![Alt](/figures/control_27572_64km.png)

### Ile-de-France region from metropolitan France in lat/lon projection

~~~bash
## We print the columns, rows, select to find bounds and we build the mask.
data_test=data/gadm36_FRA_shp/gadm36_FRA_1.shp
./shp2ncmask.py -i $data_test -lc ## --list--columns
./shp2ncmask.py -i $data_test -dc NAME_1 ## --describe-column
./shp2ncmask.py -i $data_test -s NAME_1 'Île-de-France' -b
./shp2ncmask.py -m weight -i $data_test -s NAME_1 'Île-de-France' -g 1.4,3.6,0.05,48.1,49.3,0.05 -o data/mask_IDF_4326.nc -fig figures/control_IDF_4326.png -fepsg 4326
~~~

![Alt](/figures/control_IDF_4326.png)


### Ile-de-France region from metropolitan France in LambertII projection

~~~bash
## The last is also the IDF, but in LambertII coordinates, so we change the input epsg to find the bounds
data_test=data/gadm36_FRA_shp/gadm36_FRA_1.shp
./shp2ncmask.py -i $data_test -s NAME_1 'Île-de-France' -iepsg 27572 -b
./shp2ncmask.py -m weight -i $data_test -s NAME_1 'Île-de-France' -g 534000,700000,8000,2340000,2480000,8000 -o data/mask_IDF_27572.nc -oepsg 27572 -fig figures/control_IDF_27572_8km.png -fepsg 4326
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

