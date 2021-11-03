
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


###############
## Functions ##
###############

class MethodError(Exception):
	def __init__( self , arg , default_arg ):
		self.message = "Error: the method argument '{}' must be in '{}'".format(arg,"','".join(default_arg) )
		super().__init__()

class GridError(Exception):
	def __init__( self , grid ):
		self.message = "Error: the grid '{}' must be in the format 'xmin,xmax,dx,ymin,ymax,dy'".format(grid)
		super().__init__()

class IFileError(Exception):
	def __init__( self , ifile ):
		self.message = "Error: the input file '{}' is not a file.".format(ifile)
		super().__init__()

class IFileTypeError(Exception):
	def __init__( self , ifile ):
		self.message = "Error: the input file '{}' is not a shapefile.".format(ifile)
		super().__init__()

class OFilePathError(Exception):
	def __init__( self , path , pathfile ):
		self.message = "Error: the directory '{}' of the output file '{}' is not valid.".format(path,pathfile)
		super().__init__()

class OFileTypeError(Exception):
	def __init__( self , ofile ):
		self.message = "Error: the output file '{}' is not a netcdf file.".format(ofile)
		super().__init__()

class PpeValueError(Exception):
	def __init__( self , ppe ):
		self.message = "Error: the point-per-edge '{}' must be at least equal to 2.".format(ppe)
		super().__init__()

