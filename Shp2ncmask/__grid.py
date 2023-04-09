
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

import itertools as itt
import datetime as dt
import logging
import numpy     as np
import geopandas as gpd
from shapely.geometry import Point,MultiPoint,Polygon,MultiPolygon
import pyproj

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
for mod in ["numpy","geopandas","fiona"]:
	logging.getLogger(mod).setLevel(logging.ERROR)


###############
## Functions ##
###############


class Grid:
	"""
	Class which represents a grid.
	
	- xparams is a list of three values describing the x-axis: [xmin,xmax,dx]
	- yparams is a list of three values describing the y-axis: [ymin,ymax,dy]
	- x is the array of center of the grid along the x-axis
	- y is the array of center of the grid along the x-axis
	- X and Y are the grid in 2d form
	- sq is a GeoDataFrame describing all cells as polygon.
	- pt is a GeoDataFrame describing all center of the cells
	- lat is the array (1d or 2d) of latitude, equal to y if epsg == 4326
	- lon is the array (1d or 2d) of longitude, equal to x if epsg == 4326
	"""
	
	def __init__( self , xparams , yparams , epsg = 4326 , ppe = 100 ):##{{{
		
		logger.info(f"shp2ncmask:Grid:__init__:start")
		time0 = dt.datetime.utcnow()
		
		
		self.xparams = xparams
		self.yparams = yparams
		self.epsg    = epsg
		self.ppe     = ppe ## point per edge
		
		self.x  = np.arange( self.xmin , self.xmax + self.dx / 2 , self.dx )
		self.y  = np.arange( self.ymin , self.ymax + self.dy / 2 , self.dy )
		X,Y     = np.meshgrid(self.x,self.y)
		self.X  = X.ravel()
		self.Y  = Y.ravel()
		logger.info(" * Build projected squares")
		self.sq = gpd.GeoDataFrame( [ {"geometry" : Polygon(self.build_square(x,y)) }  for x,y in zip(self.X,self.Y) ] , crs = "EPSG:{}".format(self.epsg) )
		self.sq["INDEX"] = range(self.nx*self.ny)
		
		logger.info(" * Build projected points")
		self.pt = gpd.GeoDataFrame( [ {"geometry" : Point(x,y) }  for x,y in zip(self.X,self.Y) ] , crs = "EPSG:{}".format(self.epsg) )
		self.pt["INDEX"] = range(self.nx*self.ny)
		
		self.lat = None
		self.lon = None
		self._build_latlon()
		
		self.lat_bnds = None
		self.lon_bnds = None
		self._build_latlon_bnds()
		
		time1 = dt.datetime.utcnow()
		logger.info(f"shp2ncmask:Grid:__init__:walltime:{time1-time0}")
		logger.info(f"shp2ncmask:Grid:__init__:end")
		
	##}}}
	
	def build_square( self , x , y ): ##{{{
		xy_lt = np.array( [x-self.dx/2,y+self.dy/2] )
		xy_rt = np.array( [x+self.dx/2,y+self.dy/2] )
		xy_lb = np.array( [x-self.dx/2,y-self.dy/2] )
		xy_rb = np.array( [x+self.dx/2,y-self.dy/2] )
		
		sq = []
		for g in np.linspace(0,1,self.ppe)[:-1]:
			sq.append( (1-g) * xy_lt + g * xy_rt )
		for g in np.linspace(0,1,self.ppe)[:-1]:
			sq.append( (1-g) * xy_rt + g * xy_rb )
		for g in np.linspace(0,1,self.ppe)[:-1]:
			sq.append( (1-g) * xy_rb + g * xy_lb )
		for g in np.linspace(0,1,self.ppe)[:-1]:
			sq.append( (1-g) * xy_lb + g * xy_lt )
		
		return sq
	##}}}
	
	def _build_latlon(self):##{{{
		if self.epsg == "4326":
			self.lon,self.lat = self.x,self.y
			return
		
		logger.info(" * Build lat-lon coordinates")
		
		latlon   = np.array( [ np.asarray(geo.coords) for geo in self.pt.to_crs( epsg = 4326 )["geometry"] ] ).reshape(-1,2)
#		latlon   = np.array( [ np.array( geo.array_interface()["data"]) for geo in self.pt.to_crs( epsg = 4326 )["geometry"] ] ).reshape(-1,2)
		self.lon = latlon[:,0].reshape(self.ny,self.nx)
		self.lat = latlon[:,1].reshape(self.ny,self.nx)
		
	##}}}
	
	def _build_latlon_bnds(self):##{{{
		if self.epsg == "4326":
			return
		logger.info(" * Build lat-lon bounds")
		self.lat_bnds = np.zeros( (self.y.size,self.x.size,4) ) + np.nan
		self.lon_bnds = np.zeros( (self.y.size,self.x.size,4) ) + np.nan
		
		transf = pyproj.Transformer.from_crs( int(self.epsg) , 4326 )
		for j,i in itt.product(range(self.y.size),range(self.x.size)):
			for ji,sy,sx in zip([0,1,2,3],[-1,-1,1,1],[-1,1,1,-1]):
				self.lat_bnds[j,i,ji],self.lon_bnds[j,i,ji] = transf.transform( yy = self.y[j] + sy * self.dy / 2 , xx = self.x[i] + sx * self.dx / 2 )
		
		
		
	##}}}
	
	## Properties ##{{{
	@property
	def xmin(self):
		return self.xparams[0]
	
	@property
	def xmax(self):
		return self.xparams[1]
	
	@property
	def dx(self):
		return self.xparams[2]
	
	@property
	def nx(self):
		return self.x.size
	
	@property
	def ymin(self):
		return self.yparams[0]
	
	@property
	def ymax(self):
		return self.yparams[1]
	
	@property
	def dy(self):
		return self.yparams[2]
	
	@property
	def ny(self):
		return self.y.size
	
	##}}}

