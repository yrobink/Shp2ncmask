
## Copyright(c) 2021 Yoann Robin
## 
## This file is part of Shp2ncmask.
## 
## Shp2ncmask is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Shp2ncmask is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with Shp2ncmask.  If not, see <https://www.gnu.org/licenses/>.

from .__release import version
from .__release import author_doc
from .__release import license
from .__release import src_url


doc_shp2ncmask = """
      _          ____                                 _    
  ___| |__  _ __|___ \ _ __   ___ _ __ ___   __ _ ___| | __
 / __| '_ \| '_ \ __) | '_ \ / __| '_ ` _ \ / _` / __| |/ /
 \__ \ | | | |_) / __/| | | | (__| | | | | | (_| \__ \   < 
 |___/_| |_| .__/_____|_| |_|\___|_| |_| |_|\__,_|___/_|\_\\
           |_|                                             

shp2ncmask is a tools to transform a shapefile in a netcdf file. Several methods
are proposed, and the input/output projections can be customized.


Parameters
----------

-i (or --input) [string]
    The input shapefile.
-g (or --grid) [comma separated float]
    Grid used. See the grid section.
-o (or --output) [string]
    The output netcdf file.


Optional parameters
-------------------

--help
    Print the documentation.
-b (or --bounds)
    Print the bounds of input file and quit. Can be used with '-s' and '-iepsg'.
-lc (or --list-columns)
    List the columns of the shapefile and quit.
-dc (or --describe-column)
    Describe values of a column.
-s (or --select) [string and string]
    Select a row of a column. Must be pass as '-s COL_NAME ROW_NAME'
-m (or --method) [string] default is 'point'.
    Method used to build the mask. See the method section.
--threshold [float] default is 0.8
    Threshold used by the method 'threshold'.
-iepsg (or --input-epsg) [int] default is 4326.
    epsg code of the input shapefile.
-oepsg (or --output-epsg) [int] default is 4326.
    epsg code of the output mask.
--point-per-edge [int] default is 100.
    Point per edge, see grid section.
-fig (or --figure) [string]
    File of a figure which plot the mask.
-fepsg (or --figure-epsg) default is 4326.
    epsg code of the figure.
--debug [Nothing or int]
    Enable the debug mode. Default level is 1 (print only the steps of the main
    function), a value of 2 prints the steps of the functions called by the main
    function, a value of 3 the steps of the functions called by functions, etc.

About epsg
----------

The EPSG (European Petroleum Survey Group) is a code to identify a cartographic
projection. For example:
- epsg:4326 is the classic latitude / longitude projection (also called WGS 84)
- epsg:27572 is a deprecated Lambert projection, but still widely used to
  represent metropolitan France. 
- epsg:3395 is the Mercator projection.
- see https://spatialreference.org/ for a list of epsg projections.


Grid
----

The grid is represented by 6 comma separated values taking the form:
    -g xmin,xmax,dx,ymin,ymax,dy
where:
- xmin is the min value of the x-axis,
- xmax is the max value of the x-axis,
- dx is the step between xmin and xmax,
- ymin is the min value of the y-axis,
- ymax is the max value of the y-axis,
- dy is the step between xmin and xmax.

Note 1: The first point of the x-axis is xmin, but the last point is the
maximal value of the form 'xmin + N * dx' lower than 'xmax + dx / 2' (and the
same for the y-axis).

Note 2: To compute the area, cells are re-projected in the Mercator projection.
Thus a cell defined by the four corners is again a cell in the Mercator
projection, but which not represente the area of the original projection. To
overcome this problem, a cell is not defined by only its four corners, but each
edge of each cell is defined by '--point-per-edge' points, equally spaced
between the corners. The default value of '--point-per-edge' is equal to 100.


Methods
-------

'point'
    Each grid cell is represented by its center. The value is equal to 1 if the
    center is in the interior of the polygons defined by the shapefile, 0
    otherwise.
'weight'
    The value of each grid cell is the percent of area defined by the
    intersection of the polygons of the shapefile and the cell.
'threshold'
    Start from the 'weight' mask, all values greater than the '--threshold' are
    replaced by 1, 0 otherwise.
'interior'
    Start from the 'weight' mask, all values lower than 1 are replaced by 0.
    This correspond to assign 1 only at cells inside the polygons defined by
    the shapefile.
'exterior'
    Start from the 'weight' mask, all values greater than 0 are replaced by 1.
    This correspond to assign 0 only at cells outside the polygons defined by
    the shapefile.


Shapefile sources
-----------------

Two (not exhaustive) sources of shapefile are Natural Earth and GADM-3.6:
- https://www.naturalearthdata.com/
- https://gadm.org/download_country_v3.html


License {}
-------{}

Copyright(c) 2021 Yoann Robin

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


Sources and author
------------------

- Sources are available at {}.
- Author(s): {}.

version {}
""".format(license,"-"*(len(license)+1),src_url,author_doc,version)

