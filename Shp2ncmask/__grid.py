
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

import numpy     as np
import geopandas as gpd

from shapely.geometry import Point,MultiPoint,Polygon,MultiPolygon

###############
## Functions ##
###############


class Grid:
	
	def __init__( self , xparams , yparams , epsg = 4326 , ppe = 100 ):##{{{
		self.xparams = xparams
		self.yparams = yparams
		self.epsg    = epsg
		self.ppe     = ppe ## point per edge
		
		self.x  = np.arange( self.xmin , self.xmax + self.dx / 2 , self.dx )
		self.y  = np.arange( self.ymin , self.ymax + self.dy / 2 , self.dy )
		X,Y     = np.meshgrid(self.x,self.y)
		self.X  = X.ravel()
		self.Y  = Y.ravel()
		self.sq = gpd.GeoDataFrame( [ {"geometry" : Polygon(self.build_square(x,y)) }  for x,y in zip(self.X,self.Y) ] , crs = "EPSG:{}".format(self.epsg) )
		self.sq["INDEX"] = range(self.nx*self.ny)
		
		self.pt = gpd.GeoDataFrame( [ {"geometry" : Point(x,y) }  for x,y in zip(self.X,self.Y) ] , crs = "EPSG:{}".format(self.epsg) )
		self.pt["INDEX"] = range(self.nx*self.ny)
		
		self.lat = None
		self.lon = None
		self._build_latlon()
		
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
		
		latlon   = np.array( [ np.array( geo.array_interface()["data"]) for geo in self.pt.to_crs( epsg = 4326 )["geometry"] ] ).reshape(-1,2)
		self.lon = latlon[:,0].reshape(self.ny,self.nx)
		self.lat = latlon[:,1].reshape(self.ny,self.nx)
		
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

