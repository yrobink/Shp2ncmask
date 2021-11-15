
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

import sys,os
import pyproj

import geopandas as gpd

from .__doc        import doc_shp2ncmask
from .__exceptions import *
from .__grid       import Grid
from .__mask       import build_mask
from .__mask       import mask_to_dataset
from .__plot       import build_figure


###############
## Functions ##
###############

def arguments( argv ):##{{{
	"""
	This function is used to read and check args given by the users.
	"""
	kwargs = {}
	kwargs["help"]      = False
	kwargs["col"]       = False
	kwargs["bounds"]    = False
	kwargs["method"]    = "point"
	kwargs["threshold"] = 0.8
	kwargs["iepsg"]     = "4326"
	kwargs["oepsg"]     = "4326"
	kwargs["fepsg"]     = "4326"
	kwargs["ppe"]       = 100
	kwargs["debug"]     = 0
	
	## Describe a column ?
	dc = False
	
	## Step 0: debug mode ?
	##=====================
	read_index = []
	if "--debug" in argv:
		i = argv.index("--debug")
		kwargs["debug"] = 1
		read_index = read_index + [i]
		try:
			kwargs["debug"] = int(argv[i+1])
			read_index = read_index + [i+1]
		except:
			pass
	
	## First transform arg in dict
	##============================
	if kwargs["debug"] > 1:
		print( "debug::__exec.arguments: transform argv to dict" , file = sys.stderr )
	for i,arg in enumerate(argv):
		if arg in ["--help"]:
			kwargs["help"] = True
			read_index = read_index + [i]
		if arg in ["-b","--bounds"]:
			kwargs["bounds"] = True
			read_index = read_index + [i]
		if arg in ["-lc","--list-columns"]:
			kwargs["col"] = True
			read_index = read_index + [i]
		if arg in ["-dc","--describe-column"]:
			kwargs["row"] = argv[i+1]
			dc = True
			read_index = read_index + [i,i+1]
		if arg in ["-s","--select"]:
			kwargs["select"] = [argv[i+1],argv[i+2]]
			read_index = read_index + [i,i+1,i+2]
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
		if arg in ["--point-per-edge"]:
			kwargs["ppe"] = argv[i+1]
			read_index = read_index + [i,i+1]
		if arg in ["-fig","--figure"]:
			kwargs["fig"] = argv[i+1]
			read_index = read_index + [i,i+1]
		if arg in ["-fepsg","--figure-epsg"]:
			kwargs["fepsg"] = argv[i+1]
			read_index = read_index + [i,i+1]
	
	## Check if all arguments are used
	##================================
	if kwargs["debug"] > 1:
		print( "debug::__exec.arguments: check if all arguments are used" , file = sys.stderr )
	not_read_index = [ i for i in range(len(argv)) if i not in read_index]
	if len(not_read_index) > 0:
		print( "Warning: arguments '{}' not used.".format("','".join([argv[i] for i in not_read_index])), file = sys.stderr )
	
	## Special case 1: user ask help
	##==============================
	if kwargs["help"]:
		return kwargs,True
	
	## Check arguments
	##================
	if kwargs["debug"] > 1:
		print( "debug::__exec.arguments: try/except of arguments" , file = sys.stderr )
	arg_valid = True
	
	## input epsg
	try:
		p = pyproj.Proj("epsg:{}".format(kwargs["iepsg"]))
	except pyproj.crs.CRSError:
		print( "Error: input epsg:{} is not valid".format(kwargs["iepsg"]) , file = sys.stderr )
		arg_valid = False
	
	## input file
	try:
		if not os.path.isfile(kwargs["input"]):
			raise IFileError(kwargs["input"])
		ifileext = kwargs["input"].split(".")[-1]
		if not ifileext == "shp":
			raise IFileTypeError(kwargs["input"])
	except KeyError:
		print( "Error: no input file given." , file = sys.stderr )
		arg_valid = False
	except IFileError as e:
		print( e.message , file = sys.stderr )
		arg_valid = False
	except IFileTypeError as e:
		print( e.message , file = sys.stderr )
		arg_valid = False
	
	## Special case: list/describe columns or bounds
	if kwargs["col"] or dc or kwargs["bounds"]:
		return kwargs,arg_valid
	
	## Method
	l_method  = ["point","weight","threshold","interior","exterior"]
	try:
		if kwargs["method"] not in l_method:
			raise MethodError( kwargs["method"] , l_method )
	except MethodError as e:
		print( e.message , file = sys.stderr )
		arg_valid = False
	
	## threshold
	try:
		kwargs["threshold"] = float(kwargs["threshold"])
	except ValueError:
		print( "Error: the threshold '{}' is not castable to float.".format(kwargs["threshold"]) , file = sys.stderr )
		arg_valid = False
	
	## Grid
	try:
		g = [float(x) for x in kwargs["grid"].split(",")]
		if not len(g) == 6:
			raise GridError( kwargs["grid"] )
	except KeyError:
		if not kwargs["col"]:
			print( "Error: no grid given." , file = sys.stderr )
			arg_valid = False
	except ValueError:
		if not kwargs["col"]:
			print( "Error: at least one values of the grid '{}' is not castable to float.".format(kwargs["grid"]) , file = sys.stderr )
			arg_valid = False
	except GridError as e:
		print( e.message , file = sys.stderr )
		arg_valid = False
	else:
		kwargs["grid"] = [g[:3],g[3:]]
	
	## output epsg
	try:
		p = pyproj.Proj("epsg:{}".format(kwargs["oepsg"]))
	except pyproj.crs.CRSError:
		print( "Error: output epsg:{} is not valid".format(kwargs["oepsg"]) , file = sys.stderr )
		arg_valid = False
	
	## output file
	try:
		path = os.path.sep.join( kwargs["output"].split(os.path.sep)[:-1] )
		if len(path) == 0: path = "."
		ofile = kwargs["output"].split(os.path.sep)[-1]
		if not os.path.isdir(path) and not kwargs["col"]:
			raise OFilePathError(path,kwargs["output"])
		if not ofile.split(".")[-1] == "nc":
			raise OFileTypeError(ofile)
	except KeyError:
		if not kwargs["col"]:
			print( "Error: no output file given." , file = sys.stderr )
			arg_valid = False
	except OFilePathError as e:
		print( e.message , file = sys.stderr )
		arg_valid = False
	except OFileTypeError as e:
		print( e.message , file = sys.stderr )
		arg_valid = False
	
	## Point per edge
	try:
		kwargs["ppe"] = int(kwargs["ppe"])
		if kwargs["ppe"] < 2:
			raise PpeValueError(kwargs["ppe"])
	except ValueError:
		print( "Error: the point-per-edge parameter '{}' is not castable to int.".format(kwargs["ppe"]) , file = sys.stderr )
		arg_valid = False
	except PpeValueError as e:
		print( e.message , file = sys.stderr )
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
		print( e.message , file = sys.stderr )
		arg_valid = False
	
	## output figure epsg
	try:
		p = pyproj.Proj("epsg:{}".format(kwargs["fepsg"]))
	except pyproj.crs.CRSError:
		print( "Error: plot epsg:{} is not valid".format(kwargs["fepsg"]) , file = sys.stderr )
		arg_valid = False
	
	## Final debug list
	if kwargs["debug"] > 1:
		print( "debug::__exec.arguments: list of identified parameters:" , file = sys.stderr )
		for key in kwargs:
			print( "   * {}: {}".format(key,kwargs[key]) , file = sys.stderr )
	
	return kwargs,arg_valid
##}}}

def start_shp2ncmask():##{{{
	"""
	Toolchain.
	"""
	
	## Read args
	##==========
	kwargs,arg_valid = arguments(sys.argv[1:])
	
	if not arg_valid:
		print( "Arguments not valid, abort.\nTry 'shp2ncmask --help'." , file = sys.stderr )
		sys.exit(1)
	
	## Special case 1
	##===============
	if kwargs["help"]:
		print(doc_shp2ncmask)
		sys.exit()
	
	## Extract kwargs
	##===============
	method    = kwargs.get("method")
	threshold = kwargs.get("threshold")
	iepsg     = kwargs.get("iepsg")
	oepsg     = kwargs.get("oepsg")
	ifile     = kwargs.get("input")
	ofile     = kwargs.get("output")
	grid_par  = kwargs.get("grid")
	ppe       = kwargs.get("ppe")
	select    = kwargs.get("select")
	debug     = kwargs.get("debug")
	
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
	dmask,encoding = mask_to_dataset( mask , grid , oepsg , method )
	dmask.to_netcdf( ofile , encoding = encoding )
	
	## Figure
	##=======
	figf  = kwargs.get("fig")
	if figf is not None:
		if debug > 0: print( "debug::__exec.start_shp2ncmask: figure" , file = sys.stderr )
		build_figure( figf , kwargs["fepsg"] , oepsg , grid , ish , mask , method )
	
	sys.exit()
##}}}


