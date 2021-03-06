#!/bin/bash

## First check or load example data
##=================================
data_test=data/gadm36_FRA_shp/gadm36_FRA_0.shp
data_test_zip=gadm36_FRA_shp.zip
if [ ! -f $data_test ]
then
	if [ ! -d data ]
	then
		mkdir data
	fi
	if [ ! -f data/$data_test_zip ]
	then
		wget https://biogeo.ucdavis.edu/data/gadm3.6/shp/gadm36_FRA_shp.zip -P data/
	fi
	unzip data/$data_test_zip -d data/gadm36_FRA_shp/
fi

## Print the documentation
##========================
shp2ncmask --help

## Now build four masks
##=====================
## The first is a mask in a lat lon grid on France
## The second use the Lambert Zone II projection, the figure is re-projected on lat lon coordinates.
## The two masks use a lat lon shapefile, so the iepsg is 4326
## The two masks use the weight method, i.e. the values are the percentage of area for each cell
shp2ncmask -m weight -i $data_test -iepsg 4326 -o data/mask_4326.nc -g -5,10,0.5,41,52,0.5 -oepsg 4326 -fig figures/control_4326.png -fepsg 4326
shp2ncmask -m weight -i $data_test -iepsg 4326 -o data/mask_27572.nc -g 60000,1196000,64000,1617000,2681000,64000 -oepsg 27572 -fig figures/control_27572_64km.png -fepsg 4326

## The third is an example for a selection, we want only the IDF.
## We print the columns, rows, select to find bounds and we build the mask.
shp2ncmask -i data/gadm36_FRA_shp/gadm36_FRA_1.shp -lc ## --list--columns
shp2ncmask -i data/gadm36_FRA_shp/gadm36_FRA_1.shp -dc NAME_1 ## --describe-column
shp2ncmask -i data/gadm36_FRA_shp/gadm36_FRA_1.shp -s NAME_1 'Île-de-France' -b
shp2ncmask -m weight -i data/gadm36_FRA_shp/gadm36_FRA_1.shp -s NAME_1 'Île-de-France' -g 1.4,3.6,0.05,48.1,49.3,0.05 -o data/mask_IDF_4326.nc -fig figures/control_IDF_4326.png -fepsg 4326

## The last is also the IDF, but in LambertII coordinates, so we change the input epsg to find the bounds
shp2ncmask -i data/gadm36_FRA_shp/gadm36_FRA_1.shp -s NAME_1 'Île-de-France' -iepsg 27572 -b
shp2ncmask -m weight -i data/gadm36_FRA_shp/gadm36_FRA_1.shp -s NAME_1 'Île-de-France' -g 534000,700000,8000,2340000,2480000,8000 -o data/mask_IDF_27572.nc -oepsg 27572 -fig figures/control_IDF_27572_8km.png -fepsg 4326

