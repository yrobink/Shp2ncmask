
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

import logging
import datetime  as dt
import numpy     as np
import xarray    as xr
import geopandas as gpd

from .__release import version
from .__release import src_url
from .__release import config


#############
## Logging ##
##############

## Only errors from external module
for mod in [dt,np,xr,gpd]:
	logging.getLogger(mod.__name__).setLevel(logging.ERROR)
logging.getLogger("fiona").setLevel(logging.ERROR)


###############
## Functions ##
###############

def build_mask( grid , ish , method ):##{{{
	"""
	Build the 2d mask according to the method.
	"""
	
	## Debug
	logger = logging.getLogger(__name__)
	logger.setLevel( config["logging"] )
	logger.debug("build_mask:start")
	
	## Now script
	mask = np.zeros( (grid.nx*grid.ny) )
	
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
	
	logger.debug("build_mask:end")
	return mask
##}}}

def mask_to_dataset( mask , grid , oepsg , method ):##{{{
	"""
	Transform the 2d array mask into a xarray.Dataset. Add also attributes.
	"""
	
	## Debug
	logger = logging.getLogger(__name__)
	logger.setLevel( config["logging"] )
	logger.debug("mask_to_dataset:start")
	
	if oepsg == "4326":
		amask = xr.DataArray( mask.reshape(grid.y.size,grid.x.size) , dims = ["lat","lon"] , coords = [grid.lat,grid.lon] )
		dmask = xr.Dataset( { "mask" : amask } )
	else:
		amask = xr.DataArray( mask.reshape(grid.y.size,grid.x.size) , dims = ["y","x"] , coords = [grid.y,grid.x] )
		lat   = xr.DataArray( grid.lat , dims = ["y","x"] , coords = [grid.y,grid.x] )
		lon   = xr.DataArray( grid.lon , dims = ["y","x"] , coords = [grid.y,grid.x] )
		gm_name   = grid.pt.crs.coordinate_operation.name.replace(" ","_")
		gm_method = grid.pt.crs.coordinate_operation.method_name.replace(" ","_").replace("(","").replace(")","")
		dmask = xr.Dataset( { "mask" : amask , "lat" : lat , "lon" : lon , gm_name : 1 } )
	
	## Add attributes
	##===============
	dmask.attrs["title"]         = "Mask"
	dmask.attrs["Conventions"]   = "CF-1.6"
	dmask.attrs["method"]        = method
	dmask.attrs["Shp2ncmask_url"]     = src_url
	dmask.attrs["Shp2ncmask_version"] = version
	dmask.attrs["creation_date"]      = str(dt.datetime.utcnow())[:19] + " (UTC)"
	
	dmask.lat.attrs["axis"]           = "y"
	dmask.lat.attrs["long_name"]      = "Latitude"
	dmask.lat.attrs["standard_name"]  = "latitude"
	dmask.lat.attrs["units"]          = "degrees_north"
	
	dmask.lon.attrs["axis"]           = "x"
	dmask.lon.attrs["long_name"]      = "Longitude"
	dmask.lon.attrs["standard_name"]  = "longitude"
	dmask.lon.attrs["units"]          = "degrees_east"
	
	dmask.mask.attrs["standard_name"] = "mask"
	dmask.mask.attrs["long_name"]     = "mask"
	dmask.mask.attrs["units"]         = "1"
	
	if not oepsg == "4326":
		
		dmask.mask.attrs["grid_mapping"] = gm_name
		
		dmask.x.attrs["standard_name"] = "projection_x_coordinate"
		dmask.x.attrs["long_name"]     = "x coordinate of projection"
		try:
			dmask.x.attrs["units"]         = grid.pt.crs.axis_info[0].unit_name
		except:
			pass
		
		dmask.y.attrs["standard_name"] = "projection_x_coordinate"
		dmask.y.attrs["long_name"]     = "x coordinate of projection"
		try:
			dmask.y.attrs["units"]         = grid.pt.crs.axis_info[1].unit_name
		except:
			pass
		
		dmask[gm_name].attrs["grid_mapping_name"] = gm_method
		dmask[gm_name].attrs["EPSG"]              = "{}".format(oepsg)
		dmask[gm_name].attrs["references"]        = "https://spatialreference.org/ref/epsg/{}/".format(oepsg)
	
	## Encoding
	encoding = { "lon"  : { "dtype" : "float32" , "zlib" : True , "complevel": 5 } ,
				 "lat"  : { "dtype" : "float32" , "zlib" : True , "complevel": 5 } ,
				 "mask" : { "dtype" : "float32" , "zlib" : True , "complevel": 5 } }
	
	if not oepsg == "4326":
		encoding["x"] = { "dtype" : "float32" , "zlib" : True , "complevel": 5 }
		encoding["y"] = { "dtype" : "float32" , "zlib" : True , "complevel": 5 }
		encoding[gm_name] = { "dtype" : "int32" , "zlib" : True , "complevel": 5 }
	
	logger.debug("mask_to_dataset:end")
	return dmask,encoding
##}}}

