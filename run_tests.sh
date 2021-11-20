#!/bin/bash

## Check or load example data
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

## Output dir
if [ ! -d output_tests ]
then
	mkdir output_tests
fi

## Install last version
python3 setup.py install

## Run
shp2ncmask -m weight -i $data_test -iepsg 4326 -o output_tests/mask_test.nc -g 60000,1196000,128000,1617000,2681000,128000 -oepsg 27572 -fig output_tests/fig_test.png -fepsg 4326


