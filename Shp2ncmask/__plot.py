
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

import numpy               as np
import matplotlib          as mpl
import matplotlib.pyplot   as plt
import matplotlib.gridspec as mplg
import matplotlib.colors   as mplc


###############
## Functions ##
###############

def build_figure( figf , fepsg , oepsg , grid , ish , mask , method ):
	"""
	Plot function of the mask
	"""
	
	mpl_params = dict(mpl.rcParams)
	mpl.rcdefaults()
	mpl.rcParams['font.size'] = 7
	mpl.rcParams['axes.linewidth'] = 0.5
	mpl.rcParams['lines.linewidth'] = 0.5
	mpl.rcParams['lines.markersize'] = 1
	mpl.rcParams['patch.linewidth'] = 0.5
	mpl.rcParams['xtick.major.width'] = 0.5
	mpl.rcParams['ytick.major.width'] = 0.5
	
	## Colormap
	n_step = 20
	cmap_i = plt.cm.turbo
	cmap   = mplc.ListedColormap( cmap_i(np.linspace(0.1,0.9,n_step)) )
	
	## Coordinates
	if str(grid.pt.crs.to_epsg()) == fepsg:
		XY = np.stack( (grid.X,grid.Y) , -1 )
	else:
		XY = np.array( [ np.array( geo.array_interface()["data"]) for geo in grid.pt.to_crs( epsg = fepsg )["geometry"] ] ).reshape(-1,2)
	
	## Figure
	fig = plt.figure()
	g = mplg.GridSpec( nrows = 5 , ncols = 3 )
	
	## Plot map
	ax  = fig.add_subplot(g[1,1])
	ish.to_crs(epsg=fepsg).plot( ax = ax  , facecolor = "none" , edgecolor = "black" )
	grid.sq.to_crs(epsg=fepsg).plot( ax = ax , facecolor = "none" , edgecolor = "red" )
	im = ax.scatter( XY[:,0] , XY[:,1] , c = np.floor( n_step * mask.ravel() ) / n_step , cmap = cmap )
	plt.yticks(rotation = 90)
	ax.set_xlabel( r"$x$ coordinate" )
	ax.set_ylabel( r"$y$ coordinate" )
	ax.set_title( "{} mask (proj. EPSG:{})".format(method.title(),fepsg) )
	
	## Plot colorbar
	gax = g[3,1].subgridspec( 1 , 3 , width_ratios = [0.05,1,0.05] )
	cax = fig.add_subplot(gax[0,1])
	cbar = plt.colorbar( mappable = im , cax = cax , orientation = "horizontal" , ticks = [0,0.25,0.5,0.75,1] , label = "Mask values (proj. EPSG:{})".format(oepsg) )
	cbar.ax.set_xticklabels( ["0","0.25","0.5","0.75","1"] )
	
	## Units for figsize
	mm     = 1. / 25.4
	pt     = 1. / 72
	fontsize = mpl.rcParams['font.size']*pt
	axeslw   = mpl.rcParams['axes.linewidth']*pt
	
	
	## Find width and heigh
	## The reference is the height of subplot of the map, others heights are:
	## Height for the title, , Height for x-label, height of the colorbar and height of ticks / label of the colorbar
	## Width is determined as the ratio of the subplot of the map, we add:
	## A space of y-label, a very little space to show the right black line of axis
	height_cax = 100*mm
	heights    = np.array([2*fontsize,height_cax,4.5*fontsize,1.5*fontsize,3.6*fontsize])
	height     = np.sum(heights)
	widths     = np.array([4*fontsize , height_cax / ax.get_data_ratio() / ax.get_aspect(),2*axeslw])
	width      = np.sum(widths)
	
	im.set_sizes([ 2 * min(width,height_cax) / max(grid.nx,grid.ny) / pt ])
	
	g.set_height_ratios(heights)
	g.set_width_ratios(widths)
	fig.set_figheight(height)
	fig.set_figwidth(width)
	
	## And save
	plt.subplots_adjust( left = 0 , right = 1 , bottom = 0 , top = 1 , wspace = 0 , hspace = 0 )
	plt.savefig( figf , dpi = 600 )
	plt.close(fig)
	
	## Restore mpl params
	mpl.rcParams = mpl_params

