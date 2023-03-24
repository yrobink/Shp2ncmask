
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

import logging
import datetime  as dt
import numpy     as np
import geopandas as gpd
import netCDF4
import pyproj

from .__logs      import log_start_end
from .__release   import version
from .__release   import src_url
from .__S2NParams import s2nParams


#############
## Logging ##
##############

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
for mod in ["numpy","geopandas","fiona"]:
	logging.getLogger(mod).setLevel(logging.ERROR)


###############
## Functions ##
###############

@log_start_end(logger)
def build_mask( grid , ish , method ):##{{{
	"""
	Build the 2d mask according to the method.
	"""
	
	## Now script
	mask = np.zeros( (grid.ny * grid.nx) )
	
	if method == "point":
		dI = gpd.overlay( grid.pt.to_crs(ish.crs) , ish , how = "intersection" , keep_geom_type = False )
	else:
		dI = gpd.overlay( grid.sq.to_crs(ish.crs) , ish , how = "intersection" , keep_geom_type = False )
	
	if method == "point":
		idx = dI["INDEX"].values
		mask[idx] = 1
	elif method == "weight":
		idx = dI["INDEX"].values
		mask[idx] = dI.to_crs(epsg=3395).area.values / grid.sq.loc[idx,:].to_crs(epsg=3395).area.values
	elif method == "threshold":
		idx = dI["INDEX"].values
		mask[idx] = dI.to_crs(epsg=3395).area.values / grid.sq.loc[idx,:].to_crs(epsg=3395).area.values
		mask[mask > threshold] = 1
		mask[~(mask > threshold)] = 0
	elif method == "interior":
		idx = dI["INDEX"].values
		mask[idx] = dI.to_crs(epsg=3395).area.values / grid.sq.loc[idx,:].to_crs(epsg=3395).area.values
		mask[mask < 1] = 0
	elif method == "exterior":
		idx = dI["INDEX"].values
		mask[idx] = dI.to_crs(epsg=3395).area.values / grid.sq.loc[idx,:].to_crs(epsg=3395).area.values
		mask[mask > 0] = 1
	
	return mask.reshape( (grid.ny,grid.nx) )
##}}}

def find_gm_params():##{{{
	oepsg = s2nParams.oepsg
	crs   = pyproj.crs.CRS.from_epsg(oepsg)
	
	cf_params = crs.to_cf()
	
	name = cf_params["grid_mapping_name"]
	if "lambert" in name and "conformal" in name:
		name = "Lambert_Conformal"
		attrs = {}
		for key in ["grid_mapping_name","standard_parallel","longitude_of_central_meridian","latitude_of_projection_origin","false_easting","false_northing","scale_factor"]:
			attrs[key] = str(cf_params.get(key))
	
	return name,attrs
##}}}

@log_start_end(logger)
def save_netcdf( mask , grid ):##{{{
	
	## Parameters
	method  = s2nParams.method
	ofile   = s2nParams.output
	oepsg   = s2nParams.oepsg
	
	##
	with netCDF4.Dataset( ofile , "w" ) as ncf:
		
		## Dimensions
		ncdims = {}
		ncvars = {}
		if oepsg == "4326":
			ncdims["lat"] = ncf.createDimension( "lat" , grid.lat.size )
			ncdims["lon"] = ncf.createDimension( "lon" , grid.lon.size )
			
			ncvars["lat"] = ncf.createVariable( "lat" , "double" , ("lat",) , shuffle = False , compression = "zlib" , complevel = 5 , chunksizes = (grid.lat.size,) )
			ncvars["lon"] = ncf.createVariable( "lon" , "double" , ("lon",) , shuffle = False , compression = "zlib" , complevel = 5 , chunksizes = (grid.lon.size,) )
		else:
			ncdims["y"] = ncf.createDimension( "y" , grid.y.size )
			ncdims["x"] = ncf.createDimension( "x" , grid.x.size )
			
			ncvars["y"]   = ncf.createVariable(   "y" , "double" , ("y",)    , shuffle = False , compression = "zlib" , complevel = 5 , chunksizes = (grid.y.size,) )
			ncvars["x"]   = ncf.createVariable(   "x" , "double" , ("x",)    , shuffle = False , compression = "zlib" , complevel = 5 , chunksizes = (grid.x.size,) )
			ncvars["lat"] = ncf.createVariable( "lat" , "double" , ("y","x") , shuffle = False , compression = "zlib" , complevel = 5 , chunksizes = (grid.y.size,grid.x.size) )
			ncvars["lon"] = ncf.createVariable( "lon" , "double" , ("y","x") , shuffle = False , compression = "zlib" , complevel = 5 , chunksizes = (grid.y.size,grid.x.size) )
			
			## Fill and add y / x values / attributes
			ncvars["y"][:] = grid.y[:]
			ncvars["x"][:] = grid.x[:]
			
			ncvars["y"].setncattr( "standard_name" , "projection_y_coordinate"    )
			ncvars["y"].setncattr( "long_name"     , "y coordinate of projection" )
			ncvars["x"].setncattr( "standard_name" , "projection_x_coordinate"    )
			ncvars["x"].setncattr( "long_name"     , "x coordinate of projection" )
			try:
				ncvars["y"].setncattr( "units" , grid.pt.crs.axis_info[1].unit_name )
			except:
				pass
			try:
				ncvars["x"].setncattr( "units" , grid.pt.crs.axis_info[0].unit_name )
			except:
				pass
		
		## Fill and add lat / lon values / attributes
		ncvars["lat"][:] = grid.lat[:]
		ncvars["lon"][:] = grid.lon[:]
		
		ncvars["lat"].setncattr("axis"          , "y"             )
		ncvars["lat"].setncattr("long_name"     , "Latitude"      )
		ncvars["lat"].setncattr("standard_name" , "latitude"      )
		ncvars["lat"].setncattr("units"         , "degrees_north" )
		
		ncvars["lon"].setncattr("axis"          , "x"             )
		ncvars["lon"].setncattr("long_name"     , "Longitude"    )
		ncvars["lon"].setncattr("standard_name" , "longitude"    )
		ncvars["lon"].setncattr("units"         , "degrees_east" )
		
		## Grid mapping coordinates, if needed
		if not oepsg == "4326":
			
			gm_name,gm_attrs = find_gm_params()
			
			ncvars[gm_name]    = ncf.createVariable( gm_name , "int32" )
			ncvars[gm_name][:] = 1
			for key in gm_attrs:
				ncvars[gm_name].setncattr( key , gm_attrs[key] )
			ncvars[gm_name].setncattr( "EPSG" , oepsg )
		
		## The main variable
		if not oepsg == "4326":
			ncvars["area_fraction"] = ncf.createVariable( "area_fraction" , "double" , ("y","x") , shuffle = False , compression = "zlib" , complevel = 5 , chunksizes = (grid.y.size,grid.x.size) )
			ncvars["area_fraction"].setncattr( "grid_mapping"  , gm_name )
		else:
			ncvars["area_fraction"] = ncf.createVariable( "area_fraction" , "double" , ("lat","lon") , shuffle = False , compression = "zlib" , complevel = 5 , chunksizes = (grid.lat.size,grid.lon.size) )
		
		ncvars["area_fraction"][:] = mask[:]
		
		ncvars["area_fraction"].setncattr( "standard_name" , "area_fraction" )
		ncvars["area_fraction"].setncattr( "long_name"     , "Area Fraction" )
		ncvars["area_fraction"].setncattr( "units"         , "1" )
		ncvars["area_fraction"].setncattr( "coordinates"   , "lat lon" )
		
		ncvars["area_type"] = ncf.createVariable( "area_type" , "int32" )
		ncvars["area_type"][:] = 1
		ncvars["area_type"].setncattr( "standard_name" , "all_area_types" )
		ncvars["area_type"].setncattr( "long_name"     , "All Area Types" )
		
		## Global attributes
		ncf.setncattr("title"              , "Mask" )
		ncf.setncattr("Conventions"        , "CF-1.10" )
		ncf.setncattr("method"             , method )
		ncf.setncattr("Shp2ncmask_url"     , src_url )
		ncf.setncattr("Shp2ncmask_version" , version )
		ncf.setncattr("creation_date"      , str(dt.datetime.utcnow())[:19] + " (UTC)" )
	
##}}}

