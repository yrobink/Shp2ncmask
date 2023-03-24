
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

import functools
import logging

import datetime as dt
from .__S2NParams import s2nParams


###############
## Functions ##
###############

LINE = "=" * 80

def init_logging():##{{{
	"""
	Shp2ncmask.init_logging
	=======================
	
	Function used to init the logging system
	
	"""
	
	logs_ = s2nParams.log
	
	## If at least on args, this is the loglevel / filename (if file)
	logfile = None
	if len(logs_) > 0:
		loglevel = logs_[0]
		if len(logs_) > 1:
			logfile = logs_[1]
	else:
		loglevel = logging.DEBUG
	
	## loglevel can be an integet
	try:
		numlevel = int(loglevel)
	except:
		numlevel = getattr( logging , loglevel.upper() , None )
	
	## If it is not an integer, raise an error
	if not isinstance( numlevel , int ): 
		raise Exception( f"Invalid log level: {loglevel}; nothing, an integer, 'debug', 'info', 'warning', 'error' or 'critical' expected" )
	
	##
	log_kwargs = {
		"format" : '%(message)s',
#		"format" : '%(levelname)s:%(name)s:%(funcName)s: %(message)s',
		"level" : numlevel
		}
	if logfile is not None:
		log_kwargs["filename"] = logfile
	
	logging.basicConfig(**log_kwargs)
	logging.captureWarnings(True)
##}}}

def log_start_end(plog):##{{{
	"""
	Shp2ncmask.log_start_end
	========================
	
	Decorator to add to the log the start / end of a function, and a walltime
	
	Parameters
	----------
	plog:
		A logger from logging
	
	"""
	def _decorator(f):
		
		@functools.wraps(f)
		def f_decor(*args,**kwargs):
			plog.info(f"shp2ncmask:{f.__name__}:start")
			time0 = dt.datetime.utcnow()
			out = f(*args,**kwargs)
			time1 = dt.datetime.utcnow()
			plog.info(f"shp2ncmask:{f.__name__}:walltime:{time1-time0}")
			plog.info(f"shp2ncmask:{f.__name__}:end")
			return out
		
		return f_decor
	
	return _decorator
##}}}

