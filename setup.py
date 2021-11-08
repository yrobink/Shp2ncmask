
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


## Start by import release details
from Shp2ncmask.__release import name
from Shp2ncmask.__release import version
from Shp2ncmask.__release import description
from Shp2ncmask.__release import long_description
from Shp2ncmask.__release import authors
from Shp2ncmask.__release import authors_email
from Shp2ncmask.__release import src_url
from Shp2ncmask.__release import license

## Required elements
author           = ", ".join(authors)
author_email     = ", ".join(authors_email)
packages         = ["Shp2ncmask"]
package_dir      = { "Shp2ncmask" : "Shp2ncmask" }
scripts          = ["scripts/shp2ncmask"]
requires         = [ "numpy",
					 "xarray",
					 "netCDF4",
					 "pyproj",
					 "shapely",
					 "geopandas",
					 "matplotlib"]
keywords         = ["shapefile","netcdf","mask"]
platforms        = ["linux","macosx"]
classifiers      = ["Development Status :: 4 - Beta",
					"Environment :: Console",
					"Intended Audience :: End Users/Desktop",
					"Intended Audience :: Science/Research",
					"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
					"Natural Language :: English",
					"Operating System :: Unix",
					"Programming Language :: Python :: 3 :: Only",
					"Topic :: Scientific/Engineering :: Atmospheric Science",
					"Topic :: Utilities"]


## Now the setup
from distutils.core import setup

setup(  name             = name,
		version          = version,
		description      = description,
		long_description = long_description,
		author           = author,
		author_email     = author_email,
		url              = src_url,
		packages         = packages,
		package_dir      = package_dir,
		requires         = requires,
		scripts          = scripts,
		license          = license,
		keywords         = keywords,
		platforms        = platforms,
		classifiers      = classifiers
     )
