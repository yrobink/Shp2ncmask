
## Copyright(c) 2023 Yoann Robin
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



#############
## Imports ##
#############

import os
import logging
import pyproj

## Init logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

#############
## Classes ##
#############

class S2NParams:
	"""
	Shp2ncmask.S2NParams
	====================
	
	This class contains default and user defined parameters of shp2ncmask.
	
	"""
	
	def __init__( self ):##{{{
		
		self.help              = False
		self.bounds            = False
		self.list_columns      = False
		self.describe_columns  = None
		self.select            = None
		self.log               = None
		self.input             = None
		self.output            = None
		self.grid              = None
		self.grid_mapping_name = None
		self.method            = "point"
		self.threshold         = 0.8
		self.iepsg             = "4326"
		self.oepsg             = "4326"
		self.point_per_edge    = 100
		self.figure            = None
		self.fepsg             = "4326"
	##}}}
	
	def init_from_user_inputs( self , **kwargs ):##{{{
		
		for key in self.__dict__:
			if key in kwargs:
				self.__dict__[key] = kwargs[key]
	##}}}
	
	def check(self):##{{{
		logger.info(f"shp2ncmask:S2NParams:check:start")
		
		abort = False
		try:
			
			## Start by test EPSG
			for key in [self.iepsg,self.oepsg,self.fepsg]:
				try:
					p = pyproj.Proj("epsg:{}".format(key))
				except pyproj.crs.CRSError:
					raise Exception( "Error: input epsg:{} is not valid".format(key) )
			
			## Check the method
			if not self.method in ["point","weight","threshold","interior","exterior"]:
				raise Exception( f"Error: unknow method '{self.method}'" )
			
			## Check input file
			if not os.path.isfile(self.input):
				raise FileNotFoundError(f"Input file not found: {self.input}")
			
			if not self.input.split(".")[-1] == "shp":
				raise Exception( f"Bad input file format: {self.input}")
			
			##
			if self.bounds or self.help or self.list_columns or (self.describe_columns is not None):
				pass
			else:
				
				## The grid
				g = [float(x) for x in self.grid.split(",")]
				if not len(g) == 6:
					raise Exception( f"Grid '{self.grid}' is not valid" )
				self.grid = g
				
				## Output file
				path = os.path.sep.join( self.output.split(os.path.sep)[:-1] )
				if len(path) == 0: path = "."
				ofile = self.output.split(os.path.sep)[-1]
				if not os.path.isdir(path):
					raise FileNotFoundError(f"Invalid output file: {self.output}")
				
				## Figure file
				if self.figure is not None:
					path = os.path.sep.join( self.figure.split(os.path.sep)[:-1] )
					if len(path) == 0: path = "."
					if not os.path.isdir(path):
						raise FileNotFoundError(f"Invalid figure file: {self.figure}")
				
		## All exceptions
		except Exception as e:
			if not self.help:
				logger.error(e)
			abort = True
		
		logger.info(f"shp2ncmask:S2NParams:check:end")
		
		return abort
	##}}}
	
	def keys(self):##{{{
		keys = [key for key in self.__dict__]
		keys.sort()
		return keys
	##}}}
	
	def __getitem__( self , key ):##{{{
		return self.__dict__.get(key)
	##}}}
	

s2nParams = S2NParams()

