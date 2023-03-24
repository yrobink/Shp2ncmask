#!/bin/bash

## First check or load example data
##=================================
DATA0=data/gadm41_FRA_shp/gadm41_FRA_0.shp
DATA1=data/gadm41_FRA_shp/gadm41_FRA_1.shp
DATAZ=gadm41_FRA_shp.zip
if [ ! -f $DATA0 ]
then
	if [ ! -d data ]
	then
		mkdir data
	fi
	if [ ! -f data/$DATAZ ]
	then
		wget https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_FRA_shp.zip -P data/
	fi
	unzip data/$DATAZ -d data/gadm41_FRA_shp/
fi

## Print the documentation
##========================
# shp2ncmask --help

## Now build four masks
##=====================
## The first is a mask in a lat lon grid on France
## The second use the Lambert Zone II projection, the figure is re-projected on lat lon coordinates.
## The two masks use a lat lon shapefile, so the iepsg is 4326
## The two masks use the weight method, i.e. the values are the percentage of area for each cell
shp2ncmask --method weight --input $DATA0 --iepsg 4326 --output data/mask_4326.nc  --grid -5,10,0.5,41,52,0.5 --oepsg 4326 --figure figures/control_4326.png --fepsg 4326
shp2ncmask --method weight --input $DATA0 --iepsg 4326 --output data/mask_27572.nc --grid 60000,1196000,64000,1617000,2681000,64000 --oepsg 27572 --figure figures/control_27572_64km.png --fepsg 4326

## The third is an example for a selection, we want only the IDF.
## We print the columns, rows, select to find bounds and we build the mask.
shp2ncmask --input $DATA1 --list-columns
shp2ncmask --input $DATA1 --describe-columns NAME_1
shp2ncmask --input $DATA1 --select NAME_1 'Île-de-France' --bounds
shp2ncmask --method weight --input $DATA1 --select NAME_1 'Île-de-France' --grid 1.4,3.6,0.05,48.1,49.3,0.05 --output data/mask_IDF_4326.nc --figure figures/control_IDF_4326.png --fepsg 4326

## The last is also the IDF, but in LambertII coordinates, so we change the input epsg to find the bounds
shp2ncmask --input $DATA1 --select NAME_1 'Île-de-France' --iepsg 27572 --bounds
shp2ncmask --method weight --input $DATA1 --select NAME_1 'Île-de-France' --grid 534000,700000,8000,2340000,2480000,8000 --output data/mask_IDF_27572.nc --oepsg 27572 --figure figures/control_IDF_27572_8km.png --fepsg 4326

