
## Copyright(c) 2021 / 2023 Yoann Robin
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

##############
## Packages ##
##############

import sys,os
import datetime as dt
import logging

from unidecode import unidecode

import numpy  as np
import netCDF4
import pyproj
import shapely
import geopandas as gpd

try:
	import matplotlib as mpl
except:
	mpl = None

from .__release import version
from .__logs    import LINE
from .__logs    import init_logging
from .__logs    import log_start_end

from .__inputs  import read_inputs

from .__exceptions import AbortException

from .__curses_doc import print_doc
from .__S2NParams  import s2nParams

from .__grid import Grid
from .__mask import build_mask
from .__mask import save_netcdf
from .__plot import build_figure


##################
## Init logging ##
##################

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
for mod in ["numpy","geopandas","fiona"]:
	logging.getLogger(mod).setLevel(logging.ERROR)


###############
## Functions ##
###############

def normalize_str(s):
	us = unidecode(s)
	for c in [" ","-","_","\"","\'"]:
		us = us.replace(c,"")
	return us.lower()

@log_start_end(logger)
def run_shp2ncmask():##{{{
	
	## Params
	input    = s2nParams.input
	iepsg    = s2nParams.iepsg
	oepsg    = s2nParams.oepsg
	ppe      = s2nParams.point_per_edge
	select   = s2nParams.select
	bounds   = s2nParams.bounds
	list_col = s2nParams.list_columns
	desc_col = s2nParams.describe_column
	gparams  = s2nParams.grid
	method   = s2nParams.method
	
	## Read the shapefile
	logger.info( "Read input file" )
	ish = gpd.read_file(input)
	if not str(ish.crs.to_epsg()) == iepsg:
		ish = ish.to_crs( epsg = int(iepsg) )
	
	## Bounds
	if bounds:
		logger.info( "Bounds is on, start" )
		out = "xmin;xmax;ymin;ymax\n" + \
		";".join(["{:.6f}".format(ish.bounds["minx"].min()),"{:.6f}".format(ish.bounds["maxx"].max()),"{:.6f}".format(ish.bounds["miny"].min()),"{:.6f}".format(ish.bounds["maxy"].max())])
		logger.info(out)
		print(out)
		return
	
	## List columns
	if list_col:
		logger.info( "Print list of columns" )
		out = ";".join( [c for c in ish.columns] )
		logger.info(out)
		print(out)
		return
	
	## Describe a specific column
	if desc_col is not None:
		logger.info( f"Describe column on for '{desc_col}'" )
		try:
			out = "\n".join( [str(r) for r in ish[desc_col]] )
			logger.info(out)
			print(out)
		except:
			logger.error( f"The column '{desc_col}' is not valid." )
		return
	
	## If a selection
	if select is not None:
		col,row = select
		logger.info( f"Selection of '{col}' / '{row}'..." )

		## Check if column is valid
		if col not in ish.columns:
			raise Exception( f"Column '{col}' is not a column." )
		
		## Check if row is valid
		if row not in ish[col]:
			logger.info( " * Try decoding" )
			rows  = np.unique(ish[col].values).tolist()
			urows = [normalize_str(s) for s in rows]
			urow  = normalize_str(row)
			logger.info( f" * List of unirows: " + ", ".join(urows) )
			logger.info( f" * Asked unirow: {urow}" )
			if urow not in urows:
				raise Exception( f"The row {row} is not in the column {col}" )
			row = rows[urows.index(urow)]
		
		ish = ish[ish[col] == row]
		if ish.size == 0:
			raise Exception( f"Data are empty after selection, maybe the row '{row}' is not valid ?".format(row) )
		logger.info( "Selection OK" )
	
	
	## Build the grid
	grid = Grid( gparams[:3] , gparams[3:] , epsg = oepsg , ppe = ppe )
	
	## Build the mask
	mask = build_mask( grid , ish )
	
	## Save in netcdf
	save_netcdf( mask , grid )
	
	## Figure
	if s2nParams.figure is not None:
		build_figure( grid , ish , mask )
	
##}}}

def start_shp2ncmask(*argv):##{{{
	"""
	Shp2ncmask.start_shp2ncmask
	===========================
	
	Starting point of 'shp2ncmask'.
	"""
	
	## Time counter
	walltime0 = dt.datetime.utcnow()
	
	## Read input
	read_inputs(*argv)
	
	## Init logs
	init_logging()
	logger.info(LINE)
	logger.info( "Start: {}".format(str(walltime0)[:19] + " (UTC)") )
	logger.info(LINE)
	
	## Package version
	list_pkgs = [ ("numpy"     ,np),
	              ("netCDF4"   ,netCDF4),
	              ("pyproj"    ,pyproj),
	              ("shapely"   ,shapely),
	              ("geopandas" ,gpd)
	            ]
	if mpl is not None:
		list_pkgs.append( ("matplotlib",mpl) )
	
	logger.info( "Packages version:" )
	logger.info( " * {:{fill}{align}{n}}".format( "shp2ncmask" , fill = " " , align = "<" , n = 12 ) + f"version {version}" )
	for (name_pkg,pkg) in list_pkgs:
		logger.info( " * {:{fill}{align}{n}}".format( name_pkg , fill = " " , align = "<" , n = 12 ) +  f"version {pkg.__version__}" )
	logger.info(LINE)
	
	## Serious functions start here
	try:
		## List of all input
		logger.info("Input parameters:")
		for key in s2nParams.keys():
			logger.info( " * {:{fill}{align}{n}}".format( key , fill = " ",align = "<" , n = 10 ) + ": {}".format(s2nParams[key]) )
		logger.info(LINE)
		
		## Check inputs
		abort = s2nParams.check()
		logger.info(LINE)
		
		## User asks help
		if s2nParams.help:
			print_doc()
			abort = True
		
		## In case of abort, raise Exception
		if abort:
			raise AbortException
		
		## Go!
		run_shp2ncmask()
		logger.info(LINE)
		
	except AbortException:
		pass
	except Exception as e:
		logger.error( f"Error: {e}" )
	
	## End
	walltime1 = dt.datetime.utcnow()
	logger.info( "End: {}".format(str(walltime1)[:19] + " (UTC)") )
	logger.info( "Wall time: {}".format(walltime1 - walltime0) )
	logger.info(LINE)
	

##}}}


