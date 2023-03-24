
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

import numpy  as np
import xarray as xr
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

#from .__grid       import Grid
#from .__mask       import build_mask
#from .__mask       import mask_to_dataset
#from .__plot       import build_figure


##################
## Init logging ##
##################

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


###############
## Functions ##
###############

@log_start_end(logger)
def run_shp2ncmask():##{{{
	
	return
	## Read the shapefile
	##===================
	if debug > 0:
		print( "debug::__exec.start_shp2ncmask: read shapefile" , file = sys.stderr )
	ish = gpd.read_file(ifile)
	if not ish.crs.to_epsg() == iepsg:
		ish = ish.to_crs( epsg = iepsg )
	
	## Select
	##=======
	if select is not None:
		if debug > 0: print( "debug::__exec.start_shp2ncmask: select" , file = sys.stderr )
		col,row = select
		if col not in ish.columns:
			print( "Error: '{}' is not a column. Abort.".format(col) , file = sys.stderr )
			sys.exit(1)
		ish = ish[ish[col] == row]
		if ish.size == 0:
			print( "Error: data are empty after selection, maybe the row {} is not valid ? Abort.".format(row) , file = sys.stderr )
			sys.exit(1)
	
	## Bounds
	##=======
	if kwargs["bounds"]:
		if debug > 0: print( "debug::__exec.start_shp2ncmask: bounds" , file = sys.stderr )
		print( "Bounds:" )
		print( "* xmin: {:.6f}".format(ish.bounds["minx"].min()) )
		print( "* xmax: {:.6f}".format(ish.bounds["maxx"].max()) )
		print( "* ymin: {:.6f}".format(ish.bounds["miny"].min()) )
		print( "* ymax: {:.6f}".format(ish.bounds["maxy"].max()) )
		sys.exit()
	
	## Special case 2
	##===============
	if kwargs["col"]:
		if debug > 0: print( "debug::__exec.start_shp2ncmask: print columns" , file = sys.stderr )
		print("Columns:")
		for c in ish.columns:
			print( "* {}".format(c) )
		sys.exit()
	
	## Special case 3
	##===============
	column = kwargs.get("row")
	if column is not None:
		if debug > 0: print( "debug::__exec.start_shp2ncmask: print rows of a column" , file = sys.stderr )
		try:
			rows = ish[column]
			print( "Column {}:".format(column) )
			for r in rows:
				print( "* {}".format(r) )
		except KeyError:
			print( "The column '{}' is not valid, abort.\nSee the '--list-columns' option.".format(column) , file = sys.stderr )
			sys.exit(1)
		sys.exit()
	
	## Build the grid
	##===============
	if debug > 0: print( "debug::__exec.start_shp2ncmask: build the grid" , file = sys.stderr )
	grid = Grid( grid_par[0] , grid_par[1] , epsg = oepsg , ppe = ppe )
	
	## Build the mask
	##===============
	if debug > 0: print( "debug::__exec.start_shp2ncmask: build the mask" , file = sys.stderr )
	mask = build_mask( grid , ish , method )
	
	## Transform into xarray dataset and save
	##=======================================
	if debug > 0: print( "debug::__exec.start_shp2ncmask: transform mask in dataset and save" , file = sys.stderr )
	dmask,encoding = mask_to_dataset( mask , grid , oepsg , method , kwargs.get("gm_name") )
	dmask.to_netcdf( ofile , encoding = encoding )
	
	## Figure
	##=======
	figf  = kwargs.get("fig")
	if figf is not None:
		if debug > 0: print( "debug::__exec.start_shp2ncmask: figure" , file = sys.stderr )
		build_figure( figf , kwargs["fepsg"] , oepsg , grid , ish , mask , method )
	
	logger.debug("start_shp2ncmask:end")
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
	              ("xarray"    ,xr),
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


