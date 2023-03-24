
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

## Package
##########

import os
import logging
import argparse

import pyproj

from .__logs      import log_start_end
from .__S2NParams import s2nParams

## Init logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


###############
## Functions ##
###############

def read_inputs(*argv):##{{{
	
	argv = list(argv)
	## Special case of grid
	if "--grid" in argv:
		idx = argv.index("--grid") + 1
		if argv[idx][0] == "-":
			argv[idx] = " " + argv[idx]
	
	##
	parser = argparse.ArgumentParser( add_help = False )
	
	parser.add_argument( "-h" , "--help"  , action = "store_const" , const = True , default = False )
	parser.add_argument( "--bounds"       , action = "store_const" , const = True , default = False )
	parser.add_argument( "--list-columns" , action = "store_const" , const = True , default = False )
	parser.add_argument( "--describe-columns" )
	parser.add_argument( "--select"            , nargs = 2 )
	parser.add_argument( "--log"               , nargs = '*' , default = ["WARNING"] )
	parser.add_argument( "--input"             )
	parser.add_argument( "--output"            )
	parser.add_argument( "--grid"              )
	parser.add_argument( "--method"            , default = "point" , type = str )
	parser.add_argument( "--threshold"         , default = 0.8     , type = float )
	parser.add_argument( "--iepsg"             , default = "4326"  , type = str )
	parser.add_argument( "--oepsg"             , default = "4326"  , type = str )
	parser.add_argument( "--point-per-edge"    , default = 100     , type = int )
	parser.add_argument( "--figure"            )
	parser.add_argument( "--fepsg"             , default = "4326"  , type = str )
	
	kwargs = vars(parser.parse_args(argv))
	
	s2nParams.init_from_user_inputs(**kwargs)
	
##}}}

