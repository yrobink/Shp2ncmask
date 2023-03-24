
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
import numpy               as np
import matplotlib          as mpl
import matplotlib.pyplot   as plt
import matplotlib.gridspec as mplg
import matplotlib.colors   as mplc

from .__S2NParams  import s2nParams
from .__logs import log_start_end


##################
## Init logging ##
##################

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
for mod in ["numpy","geopandas","fiona","matplotlib"]:
	logging.getLogger(mod).setLevel(logging.ERROR)


###############
## Functions ##
###############

@log_start_end(logger)
def build_figure( grid , ish , mask ):
	
	"""
	Plot function of the mask
	"""
	
	##
	ofig   = s2nParams.figure
	fepsg  = s2nParams.fepsg
	oepsg  = s2nParams.oepsg
	method = s2nParams.method
	
	## mpl params
	mpl.rcdefaults()
	mpl.rcParams['font.size'] = 7
	mpl.rcParams['axes.linewidth'] = 0.5
	mpl.rcParams['lines.linewidth'] = 0.5
	mpl.rcParams['lines.markersize'] = 1
	mpl.rcParams['patch.linewidth'] = 0.5
	mpl.rcParams['xtick.major.width'] = 0.5
	mpl.rcParams['ytick.major.width'] = 0.5
	
	## Colormap
	cmap   = mplc.ListedColormap( plt.cm.Blues(np.linspace(0.2,1,256)) )
	norm   = mplc.BoundaryNorm( np.linspace(0,1,11) , 256 )
	
	## Coordinates
	if str(grid.pt.crs.to_epsg()) == fepsg:
		XY = np.stack( (grid.X,grid.Y) , -1 )
	else:
		XY = np.array( [ np.asarray(geo.coords) for geo in grid.pt.to_crs( epsg = fepsg )["geometry"] ] ).reshape(-1,2)
	
	## Figure
	fig = plt.figure()
	g = mplg.GridSpec( nrows = 5 , ncols = 3 )
	
	## Plot map
	ax  = fig.add_subplot(g[1,1])
	ish.to_crs(epsg=fepsg).plot( ax = ax  , facecolor = "none" , edgecolor = "black" )
	grid.sq.to_crs(epsg=fepsg).plot( ax = ax , facecolor = "none" , edgecolor = "red" )
	im = ax.scatter( XY[:,0] , XY[:,1] , c = mask.ravel() , cmap = cmap , norm = norm )
	plt.yticks(rotation = 90)
	if fepsg == "4326":
		ax.set_xlabel( r"Longitude" )
		ax.set_ylabel( r"Latitude" )
	else:
		ax.set_xlabel( r"$x$ coordinate (proj. EPSG:{})".format(fepsg) )
		ax.set_ylabel( r"$y$ coordinate (proj. EPSG:{})".format(fepsg) )
	ax.set_title( "{} mask (proj. EPSG:{})".format(method.title(),oepsg) )
	
	## Plot colorbar
	gax = g[3,1].subgridspec( 1 , 3 , width_ratios = [0.05,1,0.05] )
	cax = fig.add_subplot(gax[0,1])
	cbar = plt.colorbar( mappable = im , cax = cax , orientation = "horizontal" , ticks = [0,0.25,0.5,0.75,1] , label = "Mask values" )
	cbar.ax.set_xticklabels( ["0","0.25","0.5","0.75","1"] )
	
	## Units for figsize
	mm     = 1. / 25.4
	pt     = 1. / 72
	fontsize = mpl.rcParams['font.size']*pt
	axeslw   = mpl.rcParams['axes.linewidth']*pt
	
	
	## Find width and heigh
	## The reference is the total width, equal to 100mm, then:
	## To the left of the map, an extra space of 3.8*fontsize is added for y-label
	## To the right of the map, an extra space of 2*axeslw is added to show axes
	## So, the width_ax is the width minus these values
	## Height is given by the ratio of width_ax, where ratio is a product of data ratio and aspect ratio
	## An extra space of 2*fontsize is added on the top for title
	## An extra space of 4.5*fontsize is added below for x-label and a space with colorbar
	## A space of 1.5*fontsize is added for colorbar
	## And a space of 3.6 fontsize is added for labels / title of colorbar
	width    = 100*mm
	width_ax = width - (3.8*fontsize + 2*axeslw)
	widths   = np.array([3.8*fontsize , width_ax ,2*axeslw])
	
	try:
		aspect = float(ax.get_aspect())
	except:
		aspect = 1
	height_ax  = width_ax * ax.get_data_ratio() * aspect
	heights    = np.array([2*fontsize,height_ax,4.5*fontsize,1.5*fontsize,3.6*fontsize])
	height     = np.sum(heights)
	
	## Set bullet size of grid, depending of width, height and grid size
	im.set_sizes([ 2 * min(width_ax,height_ax) / max(grid.nx,grid.ny) / pt ])
	
	## And now we set all width, height and ratios.
	g.set_height_ratios(heights)
	g.set_width_ratios(widths)
	fig.set_figheight(height)
	fig.set_figwidth(width)
	plt.subplots_adjust( left = 0 , right = 1 , bottom = 0 , top = 1 , wspace = 0 , hspace = 0 )
	
	## And save
	plt.savefig( ofig , dpi = 600 )
	plt.close(fig)


