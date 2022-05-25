
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


version_major = 1
version_minor = 1
version_patch = 0
version_extra = ""
version       = "{}.{}.{}{}".format(version_major,version_minor,version_patch,version_extra)


##

name = "shp2ncmask"


##

description      = "shp2ncmask is a tools to transform a shapefile in a netcdf file"
long_description = \
"""
shp2ncmask is a tools to transform a shapefile in a netcdf file. Several methods
are proposed, and the input/output projections can be customized.
"""


##

license = "GNU-GPL3"


##

authors       = ["Yoann Robin"]
authors_email = ["yoann.robin.k@gmail.com"]
author_doc    = ", ".join( [ ath + " ({})".format(athm) for ath,athm in zip(authors,authors_email) ] )


##

src_url = "https://github.com/yrobink/Shp2ncmask"

