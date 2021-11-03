
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

##############
## Packages ##
##############

import os
import pyproj

import geopandas as gpd

from .__exceptions import *
from .__grid       import Grid
from .__mask       import build_mask
from .__mask       import mask_to_dataset
from .__plot       import build_figure


###############
## Functions ##
###############

def arguments( argv ):##{{{
	
	kwargs = {}
	kwargs["method"]    = "point"
	kwargs["threshold"] = 0.
	kwargs["iepsg"]     = "4326"
	kwargs["oepsg"]     = "4326"
	kwargs["fepsg"]     = "4326"
	kwargs["ppe"]       = 100
	
	## First transform arg in dict
	##============================
	read_index = []
	for i,arg in enumerate(argv):
		if arg in ["-m","--method"]:
			kwargs["method"] = argv[i+1]
			read_index = read_index + [i,i+1]
		if arg == "--threshold":
			kwargs["threshold"] = argv[i+1]
			read_index = read_index + [i,i+1]
		if arg in ["-g","--grid"]:
			kwargs["grid"] = argv[i+1]
			read_index = read_index + [i,i+1]
		if arg in ["-iepsg","--input-epsg"]:
			kwargs["iepsg"] = argv[i+1]
			read_index = read_index + [i,i+1]
		if arg in ["-oepsg","--output-epsg"]:
			kwargs["oepsg"] = argv[i+1]
			read_index = read_index + [i,i+1]
		if arg in ["-i","--input"]:
			kwargs["input"] = argv[i+1]
			read_index = read_index + [i,i+1]
		if arg in ["-o","--output"]:
			kwargs["output"] = argv[i+1]
			read_index = read_index + [i,i+1]
		if arg in ["--pt-per-edge"]:
			kwargs["ppe"] = argv[i+1]
			read_index = read_index + [i,i+1]
		if arg in ["-fig","--figure"]:
			kwargs["fig"] = argv[i+1]
			read_index = read_index + [i,i+1]
		if arg in ["-fepsg","--figure-epsg"]:
			kwargs["fepsg"] = argv[i+1]
			read_index = read_index + [i,i+1]
	
	not_read_index = [ i for i in range(len(argv)) if i not in read_index]
	if len(not_read_index) > 0:
		print("""Warning: arguments '{}' not used.""".format("','".join([argv[i] for i in not_read_index])))
	
	## Check arguments
	##================
	arg_valid = True
	
	## Method
	l_method  = ["point","weight","threshold","interior","exterior"]
	try:
		if kwargs["method"] not in l_method:
			raise MethodError( kwargs["method"] , l_method )
	except MethodError as e:
		print(e.message)
		arg_valid = False
	
	## threshold
	try:
		kwargs["threshold"] = float(kwargs["threshold"])
	except ValueError:
		print( """Error: the threshold '{}' is not castable to float.""".format(kwargs["threshold"]) )
		arg_valid = False
	
	## Grid
	try:
		g = [float(x) for x in kwargs["grid"].split(",")]
		if not len(g) == 6:
			raise GridError( kwargs["grid"] )
	except KeyError:
		print( "Error: no grid given." )
		arg_valid = False
	except ValueError:
		print( """Error: at least one values of the grid '{}' is not castable to float.""".format(kwargs["grid"]) )
		arg_valid = False
	except GridError as e:
		print(e.message)
		arg_valid = False
	else:
		kwargs["grid"] = [g[:3],g[3:]]
	
	## input epsg
	try:
		p = pyproj.Proj("epsg:{}".format(kwargs["iepsg"]))
	except pyproj.crs.CRSError:
		print("Error: input epsg:{} is not valid".format(kwargs["iepsg"]))
		arg_valid = False
	
	## output epsg
	try:
		p = pyproj.Proj("epsg:{}".format(kwargs["oepsg"]))
	except pyproj.crs.CRSError:
		print("Error: output epsg:{} is not valid".format(kwargs["oepsg"]))
		arg_valid = False
	
	## input file
	try:
		if not os.path.isfile(kwargs["input"]):
			raise IFileError(kwargs["input"])
		ifileext = kwargs["input"].split(".")[-1]
		if not ifileext == "shp":
			raise OFileType(kwargs["input"])
	except KeyError:
		print( "Error: no input file given." )
		arg_valid = False
	except IFileError as e:
		print(e.message)
		arg_valid = False
	except IFileTypeError as e:
		print(e.message)
		arg_valid = False
	
	## output file
	try:
		path = os.path.sep.join( kwargs["output"].split(os.path.sep)[:-1] )
		if len(path) == 0: path = "."
		ofile = kwargs["output"].split(os.path.sep)[-1]
		if not os.path.isdir(path):
			raise OFilePathError(path,kwargs["output"])
		if not ofile.split(".")[-1] == "nc":
			raise OFileTypeError(ofile)
	except KeyError:
		print( "Error: no output file given." )
		arg_valid = False
	except OFilePathError as e:
		print(e.message)
		arg_valid = False
	except OFileTypeError as e:
		print(e.message)
		arg_valid = False
	
	## Point per edge
	try:
		kwargs["ppe"] = int(kwargs["ppe"])
		if kwargs["ppe"] < 2:
			raise PpeValueError(kwargs["ppe"])
	except ValueError:
		print( """Error: the point-per-edge parameter '{}' is not castable to int.""".format(kwargs["ppe"]) )
		arg_valid = False
	except PpeValueError as e:
		print(e.message)
		arg_valid = False
	
	## output fig file
	try:
		path = os.path.sep.join( kwargs["fig"].split(os.path.sep)[:-1] )
		if len(path) == 0: path = "."
		ofile = kwargs["fig"].split(os.path.sep)[-1]
		if not os.path.isdir(path):
			raise OFilePathError(path,kwargs["fig"])
	except KeyError:
		## If not in kwargs, no plot
		pass
	except OFilePathError as e:
		print(e.message)
		arg_valid = False
	
	## output figure epsg
	try:
		p = pyproj.Proj("epsg:{}".format(kwargs["fepsg"]))
	except pyproj.crs.CRSError:
		print("Error: plot epsg:{} is not valid".format(kwargs["fepsg"]))
		arg_valid = False
	
	return kwargs,arg_valid
##}}}

def run( argv ):##{{{
	
	## Read args
	##==========
	kwargs,arg_valid = arguments(argv)
	
	if not arg_valid:
		sys.exit("Arguments not valid, abort.")
	
	method    = kwargs["method"]
	threshold = kwargs["threshold"]
	iepsg     = kwargs["iepsg"]
	oepsg     = kwargs["oepsg"]
	ifile     = kwargs["input"]
	ofile     = kwargs["output"]
	grid_par  = kwargs["grid"]
	ppe       = kwargs["ppe"]
	
	## Read the shapefile
	##===================
	ish = gpd.read_file(ifile).set_crs( epsg = iepsg )
	
	## Build the grid
	##===============
	grid = Grid( grid_par[0] , grid_par[1] , epsg = oepsg , ppe = ppe )
	
	## Build the mask
	##===============
	mask = build_mask( grid , ish , method )
	
	## Transform into xarray dataset and save
	##=======================================
	dmask,encoding = mask_to_dataset( mask , grid , oepsg , method )
	dmask.to_netcdf( ofile , encoding = encoding )
	
	## Figure
	##=======
	figf  = kwargs.get("fig")
	if figf is not None:
		build_figure( figf , kwargs["fepsg"] , oepsg , grid , ish , mask , method )
	
##}}}


