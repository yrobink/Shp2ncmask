# Shp2ncmask

Tools to transform a shapefile in a netcdf mask. The grid, input and output
projections can be customized.

## Examples
Two examples are given in the file `run_examples`.

The first uses the command

~~~bash
data_test=data/gadm36_FRA_shp/gadm36_FRA_0.shp
./shp2ncmask.py -m weight -i $data_test -iepsg 4326 -o data/mask_4326.nc -g -5,10,0.5,41,52,0.5 -oepsg 4326 -fig figures/control_4326.png -fepsg 4326
~~~

and produces the following mask:

![Alt](/figures/control_4326.png)

The second uses the command:

~~~bash
data_test=data/gadm36_FRA_shp/gadm36_FRA_0.shp
./shp2ncmask.py -m weight -i $data_test -iepsg 4326 -o data/mask_27572.nc -g 60000,1196000,64000,1617000,2681000,64000 -oepsg 27572 -fig figures/control_27572_64km.png -fepsg 4326
~~~

and produces the following mask:

![Alt](/figures/control_27572_64km.png)



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

